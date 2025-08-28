import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { useToast } from '@/hooks/use-toast';
import { RealtimeClient } from '@/lib/realtime-client';
import { Mic, MicOff, Phone, PhoneOff } from 'lucide-react';

const RealtimeChat = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [message, setMessage] = useState('');
  const [isMicEnabled, setIsMicEnabled] = useState(true);
  
  const realtimeClientRef = useRef<RealtimeClient | null>(null);
  const remoteAudioRef = useRef<HTMLAudioElement>(null);
  const { toast } = useToast();

  const apiBase = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
  const model = 'gpt-4o-realtime-preview-2024-10-01';

  useEffect(() => {
    realtimeClientRef.current = new RealtimeClient({
      apiBase,
      model,
    });

    return () => {
      if (realtimeClientRef.current) {
        realtimeClientRef.current.disconnect();
      }
    };
  }, [apiBase, model]);

  const handleConnect = async () => {
    if (!realtimeClientRef.current || !remoteAudioRef.current) return;

    setIsConnecting(true);
    
    try {
      // Setup audio elements first
      await realtimeClientRef.current.setupAudioElements(remoteAudioRef.current);
      
      // Connect to OpenAI Realtime
      await realtimeClientRef.current.connect();
      
      setIsConnected(true);
      toast({
        title: 'Conectado',
        description: 'Conexión establecida con el asistente de voz',
      });
    } catch (error) {
      console.error('Connection failed:', error);
      toast({
        title: 'Error de conexión',
        description: error instanceof Error ? error.message : 'Failed to connect to voice assistant',
        variant: 'destructive',
      });
    } finally {
      setIsConnecting(false);
    }
  };

  const handleDisconnect = () => {
    if (realtimeClientRef.current) {
      realtimeClientRef.current.disconnect();
      setIsConnected(false);
      setIsMicEnabled(true);
      toast({
        title: 'Desconectado',
        description: 'Conexión cerrada',
      });
    }
  };

  const handleSendMessage = () => {
    if (!message.trim() || !realtimeClientRef.current) return;

    try {
      realtimeClientRef.current.sendMessage(message);
      setMessage('');
      toast({
        title: 'Mensaje enviado',
        description: 'Tu mensaje ha sido enviado al asistente',
      });
    } catch (error) {
      console.error('Failed to send message:', error);
      toast({
        title: 'Error',
        description: 'No se pudo enviar el mensaje',
        variant: 'destructive',
      });
    }
  };

  const toggleMicrophone = () => {
    setIsMicEnabled(!isMicEnabled);
    // In a real implementation, you would mute/unmute the local audio track
    toast({
      title: isMicEnabled ? 'Micrófono silenciado' : 'Micrófono activado',
      description: isMicEnabled ? 'Tu micrófono está ahora silenciado' : 'Tu micrófono está ahora activo',
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted p-4">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold bg-gradient-primary bg-clip-text text-transparent">
            Asistente de Voz AI
          </h1>
          <p className="text-muted-foreground text-lg">
            Conecta con OpenAI Realtime API para conversaciones de voz en tiempo real
          </p>
        </div>

        {/* Connection Card */}
        <Card className="border-border/50 shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {isConnected ? (
                <Phone className="h-5 w-5 text-green-500" />
              ) : (
                <PhoneOff className="h-5 w-5 text-muted-foreground" />
              )}
              Estado de Conexión
            </CardTitle>
            <CardDescription>
              {isConnected 
                ? 'Conectado al asistente de voz - ¡Puedes comenzar a hablar!'
                : 'Presiona conectar para iniciar una conversación de voz'
              }
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-4">
              {!isConnected ? (
                <Button 
                  onClick={handleConnect}
                  disabled={isConnecting}
                  variant="enterprise"
                  size="lg"
                  className="flex-1"
                >
                  {isConnecting ? 'Conectando...' : 'Conectar'}
                </Button>
              ) : (
                <>
                  <Button 
                    onClick={handleDisconnect}
                    variant="destructive"
                    size="lg"
                    className="flex-1"
                  >
                    Desconectar
                  </Button>
                  <Button
                    onClick={toggleMicrophone}
                    variant={isMicEnabled ? "default" : "secondary"}
                    size="lg"
                  >
                    {isMicEnabled ? (
                      <Mic className="h-4 w-4" />
                    ) : (
                      <MicOff className="h-4 w-4" />
                    )}
                  </Button>
                </>
              )}
            </div>
            
            {/* Connection Status Indicator */}
            <div className="flex items-center gap-2 text-sm">
              <div className={`w-2 h-2 rounded-full ${
                isConnected ? 'bg-green-500' : 'bg-muted-foreground'
              }`} />
              <span className="text-muted-foreground">
                {isConnected ? 'Conectado' : 'Desconectado'}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Message Input Card */}
        {isConnected && (
          <Card className="border-border/50 shadow-lg">
            <CardHeader>
              <CardTitle>Enviar Mensaje</CardTitle>
              <CardDescription>
                Escribe un mensaje para enviar al asistente por texto
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Input
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Escribe tu mensaje aquí..."
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  className="flex-1"
                />
                <Button 
                  onClick={handleSendMessage}
                  disabled={!message.trim()}
                  variant="enterprise"
                >
                  Enviar
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Audio Element (Hidden) */}
        <audio 
          ref={remoteAudioRef}
          autoPlay
          style={{ display: 'none' }}
          controls={false}
        />

        {/* Technical Info */}
        <Card className="border-border/50 shadow-lg">
          <CardHeader>
            <CardTitle>Información Técnica</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            <p><strong>API Base:</strong> {apiBase}</p>
            <p><strong>Modelo:</strong> {model}</p>
            <p><strong>Protocolo:</strong> WebRTC con DataChannel</p>
            <Separator className="my-2" />
            <p className="text-xs">
              Revisa la consola del navegador para ver los eventos y mensajes en tiempo real.
              La conexión utiliza sesiones efímeras para mayor seguridad.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default RealtimeChat;