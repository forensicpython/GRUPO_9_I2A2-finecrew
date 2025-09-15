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
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.ms-excel',
      'text/csv',
    ];
    
    if (!allowedTypes.includes(file.type)) {
      setError('Apenas arquivos Excel (.xlsx, .xls) e CSV são permitidos');
      return false;
    }
    
    if (file.size > 10 * 1024 * 1024) { // 10MB
      setError('Arquivo muito grande. Máximo: 10MB');
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
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Erro no upload');
      }

      const result = await response.json();
      console.log('Upload realizado com sucesso:', result);
      return true;
    } catch (error) {
      console.error('Erro no upload:', error);
      setError(error instanceof Error ? error.message : 'Erro no upload');
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
            Formatos aceitos: .xlsx, .xls, .csv (máx. 10MB)
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