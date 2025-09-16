import React, { useCallback, useState } from 'react';
import {
  Box,
  Typography,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Alert,
  Card,
  CardContent,
  Chip,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Description as FileIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';

interface UploadPageProps {
  onFilesUploaded: (files: File[]) => void;
  uploadedFiles: File[];
}

const UploadPage: React.FC<UploadPageProps> = ({
  onFilesUploaded,
  uploadedFiles,
}) => {
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState<string>('');

  const validateFile = (file: File): boolean => {
    const allowedTypes = [
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
      'application/vnd.ms-excel', // .xls
      'text/csv', // .csv
      'application/csv', // .csv (alternativo)
    ];

    // Verificar também pela extensão do arquivo (fallback)
    const allowedExtensions = ['xlsx', 'xls', 'csv'];
    const fileExtension = file.name.split('.').pop()?.toLowerCase();

    const isValidType = allowedTypes.includes(file.type);
    const isValidExtension = fileExtension && allowedExtensions.includes(fileExtension);

    if (!isValidType && !isValidExtension) {
      setError(`Apenas arquivos Excel (.xlsx, .xls) e CSV são permitidos. Arquivo: ${file.name} (tipo: ${file.type})`);
      return false;
    }

    if (file.size > 16 * 1024 * 1024) { // 16MB (igual ao backend)
      setError('Arquivo muito grande. Máximo: 16MB');
      return false;
    }

    return true;
  };

  const uploadFilesToServer = async (filesToUpload: File[]) => {
    const formData = new FormData();
    filesToUpload.forEach((file) => {
      formData.append('files', file);
    });

    try {
      console.log('📤 Enviando arquivos para upload...', filesToUpload.map(f => f.name));

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      console.log('📡 Resposta recebida:', response.status, response.statusText);

      // Verificar se a resposta é JSON válido
      const contentType = response.headers.get('content-type');
      const isJson = contentType && contentType.includes('application/json');

      if (!response.ok) {
        let errorMessage = `Erro HTTP ${response.status}: ${response.statusText}`;

        if (isJson) {
          try {
            const errorData = await response.json();
            errorMessage = errorData.error || errorMessage;
          } catch (jsonError) {
            console.warn('Erro ao parsear JSON de erro:', jsonError);
          }
        } else {
          // Se não for JSON, tentar ler como texto
          try {
            const errorText = await response.text();
            if (errorText) {
              errorMessage = errorText;
            }
          } catch (textError) {
            console.warn('Erro ao ler resposta como texto:', textError);
          }
        }

        throw new Error(errorMessage);
      }

      // Parse da resposta de sucesso
      if (isJson) {
        const result = await response.json();
        console.log('✅ Upload realizado com sucesso:', result);
        return result;
      } else {
        console.log('✅ Upload realizado com sucesso (resposta não-JSON)');
        return { success: true };
      }

    } catch (error) {
      console.error('❌ Erro no upload:', error);

      let errorMessage = 'Erro desconhecido no upload';

      if (error instanceof TypeError && error.message.includes('fetch')) {
        errorMessage = 'Erro de conexão: Verifique se o backend está rodando na porta 5001';
      } else if (error instanceof Error) {
        errorMessage = error.message;
      }

      setError(errorMessage);
      return false;
    }
  };

  const handleFiles = useCallback(async (files: FileList) => {
    setError('');
    const fileArray = Array.from(files);
    
    const validFiles = fileArray.filter(validateFile);
    
    if (validFiles.length > 0) {
      // Upload para o servidor
      const uploadSuccess = await uploadFilesToServer(validFiles);
      
      if (uploadSuccess) {
        const newFiles = [...uploadedFiles, ...validFiles];
        onFilesUploaded(newFiles);
      }
    }
  }, [uploadedFiles, onFilesUploaded]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    handleFiles(e.dataTransfer.files);
  }, [handleFiles]);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFiles(e.target.files);
    }
  };

  const removeFile = (index: number) => {
    const newFiles = uploadedFiles.filter((_, i) => i !== index);
    onFilesUploaded(newFiles);
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Box>
      <Typography variant="body1" sx={{ mb: 3, color: 'text.secondary' }}>
        Faça upload dos arquivos Excel ou CSV com dados de VR/VA para processamento.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Zona de Upload */}
      <Card
        sx={{
          mb: 3,
          border: dragOver ? '2px dashed #6366f1' : '2px dashed #374151',
          bgcolor: dragOver ? 'rgba(99, 102, 241, 0.1)' : 'transparent',
          transition: 'all 0.3s ease',
          cursor: 'pointer',
        }}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
      >
        <CardContent sx={{ textAlign: 'center', py: 4 }}>
          <UploadIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            Arraste arquivos aqui ou clique para selecionar
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Formatos aceitos: .xlsx, .xls, .csv (máx. 16MB)
          </Typography>
          <input
            type="file"
            multiple
            accept=".xlsx,.xls,.csv"
            onChange={handleFileInput}
            style={{ display: 'none' }}
            id="file-input"
          />
          <label htmlFor="file-input">
            <Button
              component="span"
              variant="contained"
              startIcon={<UploadIcon />}
            >
              Selecionar Arquivos
            </Button>
          </label>
        </CardContent>
      </Card>

      {/* Lista de Arquivos */}
      {uploadedFiles.length > 0 && (
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Arquivos Selecionados
              </Typography>
              <Chip 
                label={`${uploadedFiles.length} arquivo${uploadedFiles.length !== 1 ? 's' : ''}`}
                color="primary"
                size="small"
              />
            </Box>
            
            <List>
              {uploadedFiles.map((file, index) => (
                <ListItem
                  key={index}
                  secondaryAction={
                    <IconButton
                      edge="end"
                      onClick={() => removeFile(index)}
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                  }
                >
                  <ListItemIcon>
                    <FileIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary={file.name}
                    secondary={formatFileSize(file.size)}
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default UploadPage;