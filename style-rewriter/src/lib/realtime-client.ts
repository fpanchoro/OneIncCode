export interface EphemeralSession {
  client_secret: {
    value: string;
  };
}

export interface RealtimeConfig {
  apiBase: string;
  model: string;
}

export class RealtimeClient {
  private peerConnection: RTCPeerConnection | null = null;
  private dataChannel: RTCDataChannel | null = null;
  private localStream: MediaStream | null = null;
  private remoteAudio: HTMLAudioElement | null = null;
  private ephemeralKey: string | null = null;
  private config: RealtimeConfig;

  constructor(config: RealtimeConfig) {
    this.config = config;
  }

  async getEphemeralSession(): Promise<string> {
    const response = await fetch(`${this.config.apiBase}/session`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to get ephemeral session: ${response.statusText}`);
    }

    const session: EphemeralSession = await response.json();
    this.ephemeralKey = session.client_secret.value;
    return this.ephemeralKey;
  }

  async setupAudioElements(remoteAudioElement: HTMLAudioElement): Promise<void> {
    this.remoteAudio = remoteAudioElement;
    
    // Request microphone access
    try {
      this.localStream = await navigator.mediaDevices.getUserMedia({ 
        audio: true 
      });
    } catch (error) {
      throw new Error('Failed to access microphone. Please grant microphone permissions.');
    }
  }

  async connect(): Promise<void> {
    if (!this.ephemeralKey) {
      await this.getEphemeralSession();
    }

    if (!this.localStream || !this.remoteAudio) {
      throw new Error('Audio setup required before connecting');
    }

    // Create RTCPeerConnection
    this.peerConnection = new RTCPeerConnection({
      iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
    });

    // Add local audio track
    this.localStream.getTracks().forEach(track => {
      this.peerConnection!.addTrack(track, this.localStream!);
    });

    // Add transceiver for receiving remote audio
    this.peerConnection.addTransceiver('audio', { direction: 'recvonly' });

    // Handle remote audio stream
    this.peerConnection.ontrack = (event) => {
      console.log('Received remote track:', event);
      if (this.remoteAudio && event.streams[0]) {
        this.remoteAudio.srcObject = event.streams[0];
      }
    };

    // Create data channel
    this.dataChannel = this.peerConnection.createDataChannel('oai-events');
    
    this.dataChannel.onopen = () => {
      console.log('DataChannel opened');
      // Send initial greeting
      this.sendEvent({
        type: 'response.create',
        response: { 
          instructions: 'Hola, soy tu asistente de voz. ¿En qué te puedo ayudar?' 
        }
      });
    };

    this.dataChannel.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('Received event:', data);
      } catch (error) {
        console.error('Failed to parse event data:', error);
      }
    };

    this.dataChannel.onerror = (error) => {
      console.error('DataChannel error:', error);
    };

    // Create and send offer
    const offer = await this.peerConnection.createOffer();
    await this.peerConnection.setLocalDescription(offer);

    // Send offer to OpenAI Realtime API
    const response = await fetch(
      `https://api.openai.com/v1/realtime?model=${this.config.model}`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.ephemeralKey}`,
          'Content-Type': 'application/sdp',
        },
        body: offer.sdp,
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to connect to OpenAI Realtime: ${response.statusText}`);
    }

    const answerSdp = await response.text();
    const answer = new RTCSessionDescription({
      type: 'answer',
      sdp: answerSdp,
    });

    await this.peerConnection.setRemoteDescription(answer);
  }

  sendMessage(message: string): void {
    if (!this.dataChannel || this.dataChannel.readyState !== 'open') {
      throw new Error('DataChannel not ready');
    }

    this.sendEvent({
      type: 'response.create',
      response: { 
        instructions: message 
      }
    });
  }

  private sendEvent(event: any): void {
    if (this.dataChannel && this.dataChannel.readyState === 'open') {
      this.dataChannel.send(JSON.stringify(event));
      console.log('Sent event:', event);
    }
  }

  disconnect(): void {
    if (this.dataChannel) {
      this.dataChannel.close();
      this.dataChannel = null;
    }

    if (this.peerConnection) {
      this.peerConnection.close();
      this.peerConnection = null;
    }

    if (this.localStream) {
      this.localStream.getTracks().forEach(track => track.stop());
      this.localStream = null;
    }

    if (this.remoteAudio) {
      this.remoteAudio.srcObject = null;
    }

    this.ephemeralKey = null;
  }

  get isConnected(): boolean {
    return this.peerConnection?.connectionState === 'connected' && 
           this.dataChannel?.readyState === 'open';
  }
}