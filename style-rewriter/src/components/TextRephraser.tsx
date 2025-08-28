import React, { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { Loader2, Send, X, Sparkles } from 'lucide-react';
import { StyleOutput } from './StyleOutput';
import { rephraseText } from '@/lib/api';

interface RephrasedText {
  professional: string;
  casual: string;
  polite: string;
  social: string;
}

interface ProcessingState {
  professional: boolean;
  casual: boolean;
  polite: boolean;
  social: boolean;
}

const TextRephraser = () => {
  const [inputText, setInputText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [rephrasedTexts, setRephrasedTexts] = useState<RephrasedText>({
    professional: '',
    casual: '',
    polite: '',
    social: ''
  });
  const [processingState, setProcessingState] = useState<ProcessingState>({
    professional: false,
    casual: false,
    polite: false,
    social: false
  });
  
  const abortControllerRef = useRef<AbortController | null>(null);
  const { toast } = useToast();

  const handleProcess = async () => {
    console.log('🚀 Process Text button clicked!');
    console.log('Input text:', inputText);
    
    if (!inputText.trim()) {
      console.log('❌ No input text provided');
      toast({
        title: "Input Required",
        description: "Please enter some text to rephrase",
        variant: "destructive"
      });
      return;
    }

    try {
      console.log('⏳ Starting API call process...');
      setIsProcessing(true);
      setProcessingState({
        professional: true,
        casual: true,
        polite: true,
        social: true
      });

      // Clear previous results
      setRephrasedTexts({
        professional: '',
        casual: '',
        polite: '',
        social: ''
      });

      console.log('📡 Making API call to rephrase endpoint...');
      // Use real API call
      const results = await rephraseText(inputText);
      
      console.log('✅ API call successful! Results:', results);
      
      // Set the results
      setRephrasedTexts(results);

      // Mark all as completed
      setProcessingState({
        professional: false,
        casual: false,
        polite: false,
        social: false
      });

      toast({
        title: "Success!",
        description: "Text has been rephrased successfully",
      });

    } catch (error) {
      console.error('❌ Error in handleProcess:', error);
      toast({
        title: "Processing Error",
        description: error instanceof Error ? error.message : "Failed to process text. Please try again.",
        variant: "destructive"
      });
      // Reset processing state on error
      setProcessingState({
        professional: false,
        casual: false,
        polite: false,
        social: false
      });
    } finally {
      console.log('🏁 Process completed, setting isProcessing to false');
      setIsProcessing(false);
    }
  };

  const handleCancel = () => {
    // Cancel functionality will be handled by the mock API
    toast({
      title: "Processing Cancelled",
      description: "Text processing was cancelled",
    });
    setIsProcessing(false);
    setProcessingState({
      professional: false,
      casual: false,
      polite: false,
      social: false
    });
  };


  const clearAll = () => {
    setInputText('');
    setRephrasedTexts({
      professional: '',
      casual: '',
      polite: '',
      social: ''
    });
    setProcessingState({
      professional: false,
      casual: false,
      polite: false,
      social: false
    });
  };

  return (
    <div className="min-h-screen bg-gradient-subtle">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Sparkles className="h-8 w-8 text-primary" />
            <h1 className="text-4xl font-bold bg-gradient-primary bg-clip-text text-transparent">
              Text Rephraser AI
            </h1>
          </div>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            Transform your text into different writing styles using advanced AI. 
            Perfect for professional communication, social media, and more.
          </p>
        </div>

        {/* Input Section */}
        <Card className="mb-8 p-6 bg-gradient-card shadow-custom-lg">
          <div className="space-y-4">
            <div>
              <label htmlFor="input-text" className="block text-sm font-semibold text-foreground mb-2">
                Enter your text to rephrase
              </label>
              <Textarea
                id="input-text"
                placeholder="Hey guys, let's huddle about AI..."
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                className="min-h-[120px] resize-none text-base"
                disabled={isProcessing}
              />
            </div>
            
            <div className="flex gap-3 justify-center">
              <Button
                variant="enterprise"
                size="lg"
                onClick={handleProcess}
                disabled={isProcessing || !inputText.trim()}
                className="min-w-[140px]"
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4" />
                    Process Text
                  </>
                )}
              </Button>
              
              {isProcessing && (
                <Button
                  variant="cancel"
                  size="lg"
                  onClick={handleCancel}
                  className="min-w-[120px]"
                >
                  <X className="h-4 w-4" />
                  Cancel
                </Button>
              )}
              
              {(rephrasedTexts.professional || rephrasedTexts.casual || rephrasedTexts.polite || rephrasedTexts.social) && !isProcessing && (
                <Button
                  variant="outline"
                  size="lg"
                  onClick={clearAll}
                  className="min-w-[120px]"
                >
                  <X className="h-4 w-4" />
                  Clear All
                </Button>
              )}
            </div>
          </div>
        </Card>

        {/* Output Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <StyleOutput
            title="Professional"
            description="Formal and business-appropriate tone"
            text={rephrasedTexts.professional}
            isProcessing={processingState.professional}
            variant="professional"
          />
          
          <StyleOutput
            title="Casual"
            description="Relaxed and friendly tone"
            text={rephrasedTexts.casual}
            isProcessing={processingState.casual}
            variant="casual"
          />
          
          <StyleOutput
            title="Polite"
            description="Courteous and respectful tone"
            text={rephrasedTexts.polite}
            isProcessing={processingState.polite}
            variant="polite"
          />
          
          <StyleOutput
            title="Social Media"
            description="Engaging and shareable tone"
            text={rephrasedTexts.social}
            isProcessing={processingState.social}
            variant="social"
          />
        </div>
      </div>
    </div>
  );
};

export default TextRephraser;