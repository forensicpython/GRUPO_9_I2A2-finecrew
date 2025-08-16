import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Button,
  Chip,
  Alert,
  LinearProgress,
  Grid,
  Card,
  CardContent
} from '@mui/material';
import {
  CloudUpload,
  Description,
  CheckCircle,
  Error,
  Delete
} from '@mui/icons-material';

interface FileUploaderProps {
  onFilesUploaded: (files: File[]) => void;
  uploadedFiles: File[];
}

const requiredFiles = [
  'ATIVOS.xlsx',
  'FÉRIAS.xlsx', 
  'DESLIGADOS.xlsx',
  'ADMISSÃO ABRIL.xlsx',
  'Base sindicato x valor.xlsx'
];

const FileUploader: React.FC<FileUploaderProps> = ({ onFilesUploaded, uploadedFiles }) => {
  const [dragActive, setDragActive] = useState(false);
  
  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = [...uploadedFiles];
    
    acceptedFiles.forEach(file => {
      // Verificar se arquivo já não foi carregado
      if (!newFiles.find(f => f.name === file.name)) {
        newFiles.push(file);
      }
    });
    
    onFilesUploaded(newFiles);
  }, [uploadedFiles, onFilesUploaded]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls']
    },
    multiple: true
  });

  const removeFile = (fileToRemove: File) => {
    const newFiles = uploadedFiles.filter(file => file !== fileToRemove);
    onFilesUploaded(newFiles);
  };

  const getFileStatus = (fileName: string) => {
    const isRequired = requiredFiles.some(req => 
      fileName.toLowerCase().includes(req.toLowerCase().replace('.xlsx', ''))
    );
    const isUploaded = uploadedFiles.some(file => file.name === fileName);
    
    return { isRequired, isUploaded };
  };

  const uploadProgress = (uploadedFiles.length / requiredFiles.length) * 100;
  const allRequiredUploaded = requiredFiles.every(reqFile => 
    uploadedFiles.some(file => 
      file.name.toLowerCase().includes(reqFile.toLowerCase().replace('.xlsx', ''))
    )
  );

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      {/* Área de Upload */}
      <Box sx={{ flex: '1 1 auto' }}>
        <Paper
          {...getRootProps()}
          elevation={0}
          className={`upload-area ${isDragActive ? 'drag-active' : ''}`}
          sx={{
            p: 6,
            border: isDragActive ? '2px dashed #3b82f6' : '2px dashed #94a3b8',
            background: isDragActive 
              ? 'linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)' 
              : 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
            cursor: 'pointer',
            textAlign: 'center',
            transition: 'all 0.3s ease',
            borderRadius: 3,
            position: 'relative',
            overflow: 'hidden',
            '&:hover': {
              borderColor: '#3b82f6',
              transform: 'translateY(-2px)',
              boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
            },
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: '-100%',
              width: '100%',
              height: '100%',
              background: 'linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.1), transparent)',
              transition: 'left 0.5s',
            },
            '&:hover::before': {
              left: '100%',
            }
          }}
        >
          <input {...getInputProps()} />
          <CloudUpload 
            sx={{ 
              fontSize: 72, 
              background: 'linear-gradient(135deg, #3b82f6 0%, #1e40af 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              mb: 3,
              filter: isDragActive ? 'drop-shadow(0 4px 6px rgba(59, 130, 246, 0.3))' : 'none',
              transform: isDragActive ? 'scale(1.1)' : 'scale(1)',
              transition: 'all 0.3s ease'
            }} 
          />
          <Typography 
            variant="h5" 
            gutterBottom 
            sx={{ 
              fontWeight: 600,
              color: '#1e293b',
              mb: 1
            }}
          >
            {isDragActive ? 'Solte os arquivos aqui' : 'Arraste os arquivos Excel aqui'}
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            ou clique para selecionar arquivos
          </Typography>
          <Button 
            variant="contained" 
            size="large"
            className="btn-gradient"
            sx={{
              py: 1.5,
              px: 4,
              fontSize: '1rem',
              fontWeight: 600,
              borderRadius: 2,
              textTransform: 'none',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
              }
            }}
          >
            Selecionar Arquivos
          </Button>
          <Typography variant="caption" display="block" sx={{ mt: 2 }}>
            Aceita apenas arquivos .xlsx e .xls
          </Typography>
        </Paper>

        {/* Progress */}
        {uploadedFiles.length > 0 && (
          <Box sx={{ mt: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="body2" sx={{ mr: 2 }}>
                Progresso: {uploadedFiles.length}/{requiredFiles.length} arquivos obrigatórios
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {Math.round(uploadProgress)}%
              </Typography>
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={uploadProgress} 
              sx={{ height: 8, borderRadius: 4 }}
            />
          </Box>
        )}

        {/* Status */}
        {uploadedFiles.length > 0 && (
          <Box sx={{ mt: 2 }}>
            {allRequiredUploaded ? (
              <Alert severity="success" icon={<CheckCircle />}>
                Todos os arquivos obrigatórios foram carregados! Você pode prosseguir para o processamento.
              </Alert>
            ) : (
              <Alert severity="warning">
                Carregue todos os {requiredFiles.length} arquivos obrigatórios para continuar.
              </Alert>
            )}
          </Box>
        )}
      </Box>

      {/* Lista de Arquivos Obrigatórios */}
      <Box sx={{ flex: '0 0 auto' }}>
        <Card 
          elevation={0}
          className="hover-lift"
          sx={{ 
            background: 'white',
            border: '1px solid #e2e8f0',
            borderRadius: 3,
            overflow: 'visible'
          }}
        >
          <CardContent sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Arquivos Obrigatórios
            </Typography>
            <List dense>
              {requiredFiles.map((fileName) => {
                const isUploaded = uploadedFiles.some(file => 
                  file.name.toLowerCase().includes(fileName.toLowerCase().replace('.xlsx', ''))
                );
                
                return (
                  <ListItem key={fileName}>
                    <ListItemIcon>
                      {isUploaded ? (
                        <CheckCircle color="success" />
                      ) : (
                        <Description color="action" />
                      )}
                    </ListItemIcon>
                    <ListItemText 
                      primary={fileName}
                      secondary={isUploaded ? "Carregado" : "Pendente"}
                    />
                  </ListItem>
                );
              })}
            </List>
          </CardContent>
        </Card>
      </Box>

      {/* Lista de Arquivos Carregados */}
      {uploadedFiles.length > 0 && (
        <Box>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Arquivos Carregados ({uploadedFiles.length})
              </Typography>
              <List>
                {uploadedFiles.map((file, index) => {
                  const { isRequired } = getFileStatus(file.name);
                  const fileSize = (file.size / 1024 / 1024).toFixed(2);
                  
                  return (
                    <ListItem
                      key={index}
                      secondaryAction={
                        <Button
                          startIcon={<Delete />}
                          onClick={() => removeFile(file)}
                          color="error"
                          size="small"
                        >
                          Remover
                        </Button>
                      }
                    >
                      <ListItemIcon>
                        <Description color={isRequired ? "primary" : "action"} />
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            {file.name}
                            {isRequired && (
                              <Chip 
                                label="Obrigatório" 
                                size="small" 
                                color="primary" 
                                variant="outlined" 
                              />
                            )}
                          </Box>
                        }
                        secondary={`${fileSize} MB`}
                      />
                    </ListItem>
                  );
                })}
              </List>
            </CardContent>
          </Card>
        </Box>
      )}
    </Box>
  );
};

export default FileUploader;