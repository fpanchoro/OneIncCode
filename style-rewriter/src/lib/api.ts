// Real API call to rephrase endpoint
export const rephraseText = async (text: string) => {
  const endpoint = window.location.origin + '/v1/rephrase';
  
  console.log('Calling endpoint:', endpoint);
  console.log('Request payload:', {
    input_text: text,
    styles: ['professional', 'casual', 'polite', 'social-media']
  });

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': '1'
      },
      body: JSON.stringify({
        input_text: text,
        styles: ['professional', 'casual', 'polite', 'social-media']
      })
    });

    console.log('Response status:', response.status);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('Response data:', data);
    
    // Map API response to component format
    return {
      professional: data.results.professional,
      casual: data.results.casual,
      polite: data.results.polite,
      social: data.results['social-media']
    };
  } catch (error) {
    console.error('Fetch error:', error);
    if (error instanceof TypeError && error.message === 'Load failed') {
      throw new Error('CORS Error: No se puede conectar al servidor. Asegúrate de que el servidor esté ejecutándose en ' + endpoint + ' y tenga CORS habilitado.');
    }
    throw error;
  }
};

// Simulated streaming response using real API
export const simulateStreamingRephrase = async (
  text: string,
  onUpdate: (style: string, content: string) => void
) => {
  const responses = await rephraseText(text);
  
  for (const [style, content] of Object.entries(responses)) {
    const words = content.split(' ');
    let currentText = '';
    
    for (const word of words) {
      await new Promise(resolve => setTimeout(resolve, 100));
      currentText += (currentText ? ' ' : '') + word;
      onUpdate(style, currentText);
    }
  }
};