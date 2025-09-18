import React, { useCallback, useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Alert,
  LinearProgress,
  Chip,
  IconButton,
  Zoom,
  Slide,
} from '@mui/material';
import {
  CloudUpload,
  Description,
  Delete,
  CheckCircle,
  Error as ErrorIcon,
  Info,
} from '@mui/icons-material';

export interface UploadPageProps {
  onFilesUpload: (files: any[]) => void;
  files: any[];
}

const REQUIRED_FILES = [
  'ADMISSÃO ABRIL.xlsx',
  'Base dias uteis.xlsx',
  'Base sindicato x valor.xlsx',
  'ESTÁGIO.xlsx',
  'FÉRIAS.xlsx'
];

const UploadPage: React.FC<UploadPageProps> = ({ onFilesUpload, files }) => {
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(true);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    // Só remove dragOver se estiver saindo realmente da área
    if (!e.currentTarget.contains(e.relatedTarget as Node)) {
      setDragOver(false);
    }
  }, []);

  const handleFileUpload = async (selectedFiles: File[]) => {
    if (selectedFiles.length === 0) return;

    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      selectedFiles.forEach(file => {
        formData.append('files', file);
      });

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        onFilesUpload(data.files);
      } else {
        setError(data.error || 'Erro no upload dos arquivos');
      }
    } catch (error) {
      setError('Erro de conexão durante o upload');
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);

    const droppedFiles = Array.from(e.dataTransfer.files);
    handleFileUpload(droppedFiles);
  }, [handleFileUpload]);

  const handleFileInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      handleFileUpload(selectedFiles);
    }
  }, [handleFileUpload]);

  const handleRemoveFile = async (fileName: string) => {
    const updatedFiles = files.filter(file => file.name !== fileName);
    onFilesUpload(updatedFiles);
  };

  const getFileIcon = (fileName: string) => {
    if (fileName.endsWith('.xlsx') || fileName.endsWith('.xls')) {
      return <Description color="success" />;
    }
    return <Description color="action" />;
  };

  const isFileRequired = (fileName: string) => {
    return REQUIRED_FILES.some(required =>
      fileName.toLowerCase().includes(required.toLowerCase().split('.')[0])
    );
  };

  const getUploadedRequiredFiles = () => {
    return REQUIRED_FILES.filter(required =>
      files.some(file =>
        file.name.toLowerCase().includes(required.toLowerCase().split('.')[0])
      )
    );
  };

  const getMissingRequiredFiles = () => {
    return REQUIRED_FILES.filter(required =>
      !files.some(file =>
        file.name.toLowerCase().includes(required.toLowerCase().split('.')[0])
      )
    );
  };

  const canProceed = () => {
    return getMissingRequiredFiles().length === 0;
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
        📤 Upload dos Arquivos Excel
      </Typography>

      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Faça o upload dos 5 arquivos Excel obrigatórios para processamento do VR/VA:
      </Typography>

      {/* Required Files List */}
      <Card sx={{ mb: 3, bgcolor: 'background.paper' }}>
        <CardContent>
          <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2 }}>
            📋 Arquivos Obrigatórios
          </Typography>
          <List dense>
            {REQUIRED_FILES.map((fileName, index) => {
              const isUploaded = getUploadedRequiredFiles().includes(fileName);
              return (
                <ListItem key={index} sx={{ py: 0.5 }}>
                  <ListItemIcon>
                    {isUploaded ? (
                      <CheckCircle color="success" fontSize="small" />
                    ) : (
                      <ErrorIcon color="error" fontSize="small" />
                    )}
                  </ListItemIcon>
                  <ListItemText
                    primary={fileName}
                    sx={{
                      '& .MuiListItemText-primary': {
                        fontSize: '0.875rem',
                        color: isUploaded ? 'success.main' : 'text.secondary',
                        fontWeight: isUploaded ? 500 : 400,
                      }
                    }}
                  />
                  {isUploaded && (
                    <Chip
                      label="✓ Enviado"
                      size="small"
                      color="success"
                      variant="outlined"
                    />
                  )}
                </ListItem>
              );
            })}
          </List>
        </CardContent>
      </Card>

      {/* Upload Area */}
      <Card
        sx={{
          mb: 3,
          border: dragOver ? '2px dashed' : '2px dashed transparent',
          borderColor: dragOver ? 'primary.main' : 'grey.300',
          bgcolor: dragOver ? 'action.hover' : 'background.paper',
          transition: 'all 0.3s ease',
          cursor: 'pointer',
        }}
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <CardContent sx={{ textAlign: 'center', py: 4, pointerEvents: 'none' }}>
          <CloudUpload
            sx={{
              fontSize: 48,
              color: dragOver ? 'primary.main' : 'grey.400',
              mb: 2,
              transition: 'color 0.3s ease',
              pointerEvents: 'none'
            }}
          />
          <Typography variant="h6" gutterBottom sx={{ pointerEvents: 'none' }}>
            {dragOver ? 'Solte os arquivos aqui' : 'Arraste e solte os arquivos'}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2, pointerEvents: 'none' }}>
            ou clique para selecionar arquivos Excel (.xlsx, .xls)
          </Typography>

          <input
            type="file"
            multiple
            accept=".xlsx,.xls"
            onChange={handleFileInputChange}
            style={{ display: 'none' }}
            id="file-input"
          />
          <label htmlFor="file-input" style={{ pointerEvents: 'auto' }}>
            <Button
              variant="contained"
              component="span"
              startIcon={<CloudUpload />}
              disabled={uploading}
              sx={{ mt: 1, pointerEvents: 'auto' }}
            >
              {uploading ? 'Enviando...' : 'Selecionar Arquivos'}
            </Button>
          </label>

          {uploading && (
            <Box sx={{ mt: 2 }}>
              <LinearProgress />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Processando upload...
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Error Alert */}
      {error && (
        <Slide direction="up" in={!!error}>
          <Alert
            severity="error"
            sx={{ mb: 3 }}
            onClose={() => setError(null)}
          >
            {error}
          </Alert>
        </Slide>
      )}

      {/* Success Alert */}
      {canProceed() && (
        <Zoom in>
          <Alert severity="success" sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CheckCircle fontSize="small" />
              <Typography variant="body2">
                Todos os arquivos obrigatórios foram enviados! Você pode prosseguir para a configuração.
              </Typography>
            </Box>
          </Alert>
        </Zoom>
      )}

      {/* Uploaded Files List */}
      {files.length > 0 && (
        <Card>
          <CardContent>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2 }}>
              📁 Arquivos Enviados ({files.length})
            </Typography>
            <List>
              {files.map((file, index) => (
                <ListItem
                  key={index}
                  sx={{
                    bgcolor: 'action.hover',
                    mb: 1,
                    borderRadius: 1,
                    border: '1px solid',
                    borderColor: 'divider',
                  }}
                >
                  <ListItemIcon>
                    {getFileIcon(file.name)}
                  </ListItemIcon>
                  <ListItemText
                    primary={file.name}
                    secondary={`${(file.size / 1024 / 1024).toFixed(2)} MB`}
                    sx={{
                      '& .MuiListItemText-primary': {
                        fontWeight: 500,
                        fontSize: '0.875rem',
                      }
                    }}
                  />
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {isFileRequired(file.name) && (
                      <Chip
                        label="Obrigatório"
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    )}
                    <IconButton
                      edge="end"
                      size="small"
                      onClick={() => handleRemoveFile(file.name)}
                      sx={{ color: 'error.main' }}
                    >
                      <Delete fontSize="small" />
                    </IconButton>
                  </Box>
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}

      {/* Info Alert */}
      {files.length > 0 && !canProceed() && (
        <Alert severity="info" sx={{ mt: 3 }}>
          <Typography variant="body2">
            <strong>Arquivos faltando:</strong> {getMissingRequiredFiles().join(', ')}
          </Typography>
        </Alert>
      )}
    </Box>
  );
};

export default UploadPage;