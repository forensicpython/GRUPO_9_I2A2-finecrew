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
  sistema_usado?: string;
  metodo_calculo?: string;
  fonte_dados?: string;
}