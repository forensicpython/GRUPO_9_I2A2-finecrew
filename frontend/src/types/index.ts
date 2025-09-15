export interface GroqConfig {
  apiKey: string;
  model: string;
}

export interface ProcessingResults {
  funcionarios_elegiveis: number;
  valor_total_vr: number;
  valor_empresa: number;
  valor_funcionario: number;
  tempo_processamento: string;
  arquivos_gerados: string[];
}

export interface AppState {
  currentStep: number;
  groqConfig: GroqConfig | null;
  uploadedFiles: File[];
  processing: boolean;
  results: ProcessingResults | null;
}

export interface StepProps {
  onNext?: () => void;
  onPrevious?: () => void;
}