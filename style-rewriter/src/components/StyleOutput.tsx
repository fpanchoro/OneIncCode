import React from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Copy, Check, Briefcase, Users, Heart, Share2, Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { cn } from '@/lib/utils';

interface StyleOutputProps {
  title: string;
  description: string;
  text: string;
  isProcessing: boolean;
  variant: 'professional' | 'casual' | 'polite' | 'social';
}

const styleConfig = {
  professional: {
    icon: Briefcase,
    gradient: 'from-blue-500 to-blue-600',
    bgColor: 'bg-blue-50',
    textColor: 'text-blue-700',
    borderColor: 'border-blue-200'
  },
  casual: {
    icon: Users,
    gradient: 'from-green-500 to-green-600',
    bgColor: 'bg-green-50',
    textColor: 'text-green-700',
    borderColor: 'border-green-200'
  },
  polite: {
    icon: Heart,
    gradient: 'from-purple-500 to-purple-600',
    bgColor: 'bg-purple-50',
    textColor: 'text-purple-700',
    borderColor: 'border-purple-200'
  },
  social: {
    icon: Share2,
    gradient: 'from-orange-500 to-orange-600',
    bgColor: 'bg-orange-50',
    textColor: 'text-orange-700',
    borderColor: 'border-orange-200'
  }
};

export const StyleOutput: React.FC<StyleOutputProps> = ({
  title,
  description,
  text,
  isProcessing,
  variant
}) => {
  const [copied, setCopied] = React.useState(false);
  const { toast } = useToast();
  const config = styleConfig[variant];
  const Icon = config.icon;

  const handleCopy = async () => {
    if (!text) return;
    
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      toast({
        title: "Copied!",
        description: `${title} text copied to clipboard`,
      });
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      toast({
        title: "Copy failed",
        description: "Failed to copy text to clipboard",
        variant: "destructive"
      });
    }
  };

  return (
    <Card className={cn(
      "p-6 transition-all duration-300 hover:shadow-custom-md",
      config.borderColor,
      "border-2 bg-gradient-card"
    )}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={cn(
            "p-2 rounded-lg bg-gradient-to-r",
            config.gradient
          )}>
            <Icon className="h-5 w-5 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-lg text-foreground">{title}</h3>
            <p className="text-sm text-muted-foreground">{description}</p>
          </div>
        </div>
        
        {text && !isProcessing && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleCopy}
            className="shrink-0"
          >
            {copied ? (
              <>
                <Check className="h-4 w-4 text-success" />
                <span className="text-success">Copied</span>
              </>
            ) : (
              <>
                <Copy className="h-4 w-4" />
                Copy
              </>
            )}
          </Button>
        )}
      </div>

      {/* Content */}
      <div className="relative">
        {isProcessing && !text ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto mb-2" />
              <p className="text-sm text-muted-foreground">Generating {title.toLowerCase()} version...</p>
            </div>
          </div>
        ) : (
          <Textarea
            value={text}
            readOnly
            placeholder={`${title} version will appear here...`}
            className={cn(
              "min-h-[120px] resize-none text-base",
              config.bgColor,
              config.borderColor,
              text ? config.textColor : "text-muted-foreground"
            )}
          />
        )}
        
        {/* Processing indicator */}
        {isProcessing && text && (
          <div className="absolute bottom-2 right-2">
            <div className="flex items-center gap-1 bg-background/80 backdrop-blur-sm rounded-md px-2 py-1">
              <Loader2 className="h-3 w-3 animate-spin text-primary" />
              <span className="text-xs text-muted-foreground">Writing...</span>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};