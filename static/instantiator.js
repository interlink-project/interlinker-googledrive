const {
  CssBaseline,
  ThemeProvider,
  Typography,
  Container,
  createTheme,
  Box,
  Button,
  Input,
  LinearProgress,
  IconButton,
  Avatar,
} = MaterialUI;

var { basepath } = jQuery('#data').data();

const http = axios.create({
  headers: {
    "Content-type": "application/json"
  }
});

const bytesToSize = (bytes, decimals = 2) => {
  if (bytes === 0) {
    return '0 Bytes';
  }

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
};


class UploadFilesService {
  upload(file, onUploadProgress) {
    let formData = new FormData();

    formData.append("file", file);

    return http.post(`${basepath}/api/v1/assets/`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      onUploadProgress,
    });
  }
  confirm(id) {
    return http.post(`${basepath}/assets/${id}/persist/`, null, {});
  }
}

const uploadService = new UploadFilesService();

// Create a theme instance.
const theme = createTheme({
  components: {
    MuiInputBase: {
      styleOverrides: {
        input: {
          '&::placeholder': {
            opacity: 0.86,
            color: '#42526e'
          }
        }
      }
    }
  },
  palette: {
    action: {
      active: '#6b778c'
    },
    background: {
      default: '#f4f5f7',
      paper: '#ffffff'
    },
    error: {
      contrastText: '#ffffff',
      main: '#f44336'
    },
    mode: 'light',
    primary: {
      contrastText: '#ffffff',
      main: '#0f97c7',
      main2: '#091a22',
    },
    success: {
      contrastText: '#ffffff',
      main: '#44c949'
    },
    text: {
      primary: '#172b4d',
      secondary: '#6b778c',
      contrastMain2: '#f3f3f3'
    },
    warning: {
      contrastText: '#ffffff',
      main: '#ff9800'
    }
  },
  shadows: [
    'none',
    '0px 1px 2px rgba(0, 0, 0, 0.12), 0px 0px 0px 1px rgba(0, 0, 0, 0.05)',
    '0px 2px 4px rgba(0, 0, 0, 0.15), 0px 0px 0px 1px rgba(0, 0, 0, 0.05)',
    '0 0 1px 0 rgba(0,0,0,0.31), 0 3px 4px -2px rgba(0,0,0,0.25)',
    '0 0 1px 0 rgba(0,0,0,0.31), 0 3px 4px -2px rgba(0,0,0,0.25)',
    '0 0 1px 0 rgba(0,0,0,0.31), 0 4px 6px -2px rgba(0,0,0,0.25)',
    '0 0 1px 0 rgba(0,0,0,0.31), 0 4px 6px -2px rgba(0,0,0,0.25)',
    '0 0 1px 0 rgba(0,0,0,0.31), 0 4px 8px -2px rgba(0,0,0,0.25)',
    '0 0 1px 0 rgba(0,0,0,0.31), 0 5px 8px -2px rgba(0,0,0,0.25)',
    '0 0 1px 0 rgba(0,0,0,0.31), 0 6px 12px -4px rgba(0,0,0,0.25)',
    '0 0 1px 0 rgba(0,0,0,0.31), 0 7px 12px -4px rgba(0,0,0,0.25)',
    '0 0 1px 0 rgba(0,0,0,0.31), 0 6px 16px -4px rgba(0,0,0,0.25)',
    '0 0 1px 0 rgba(0,0,0,0.31), 0 7px 16px -4px rgba(0,0,0,0.25)',
    '0 0 1px 0 rgba(0,0,0,0.31), 0 8px 18px -8px rgba(0,0,0,0.25)',
    '0 0 1px 0 rgba(0,0,0,0.31), 0 9px 18px -8px rgba(0,0,0,0.25)',
    '0 0 1px 0 rgba(0,0,0,0.31), 0 10px 20px -8px rgba(0,0,0,0.25)',
    '0 0 1px 0 rgba(0,0,0,0.31), 0 11px 20px -8px rgba(0,0,0,0.25)',
    '0 0 1px 0 rgba(0,0,0,0.31), 0 12px 22px -8px rgba(0,0,0,0.25)',
    '0 0 1px 0 rgba(0,0,0,0.31), 0 13px 22px -8px rgba(0,0,0,0.25)',
    '0 0 1px 0 rgba(0,0,0,0.31), 0 14px 24px -8px rgba(0,0,0,0.25)',
    '0 0 1px 0 rgba(0,0,0,0.31), 0 16px 28px -8px rgba(0,0,0,0.25)',
    '0 0 1px 0 rgba(0,0,0,0.31), 0 18px 30px -8px rgba(0,0,0,0.25)',
    '0 0 1px 0 rgba(0,0,0,0.31), 0 20px 32px -8px rgba(0,0,0,0.25)',
    '0 0 1px 0 rgba(0,0,0,0.31), 0 22px 34px -8px rgba(0,0,0,0.25)',
    '0 0 1px 0 rgba(0,0,0,0.31), 0 24px 36px -8px rgba(0,0,0,0.25)'
  ]
});

function App() {
  const [progress, setProgress] = React.useState(0)
  const [file, setFile] = React.useState(null)
  const [iframeKey, setIframeKey] = React.useState(null)
  const [created, setCreated] = React.useState(null)

  var onUploadProgress = (progressEvent) => {
    setProgress(100 * progressEvent.loaded / progressEvent.total)
  }

  React.useEffect(() => {
    if (window.parent) {
      window.parent.postMessage({
        'code': 'initialized',
      }, "*");
    }
  }, [])

  const selectFile = async (event) => {
    var f = event.target.files[0]

    uploadService.upload(f, onUploadProgress).then(response => {
      console.log("RESPONSE UPLOAD", response.data);
      setFile(response.data)
      setProgress(0)
    })
  }

  const confirmFile = async () => {
    uploadService.confirm(file._id).then(response => {
      console.log("RESPONSE CONFIRM", response.data);
      setCreated(response.data)
      if (window.parent) {
        window.parent.postMessage({
          'code': 'asset_created',
          'data': response.data
        }, "*");
      }
    })
  }

  const maxFiles = 1

  // src={file.webViewLink}
  // src={`https://docs.google.com/gview?url=${file.webContentLink}&embedded=true`}

  return (
    <Container maxWidth="md">

      <div>
        {created ?
          (<Box
            sx={{
              maxWidth: 450,
              mx: 'auto',
              alignItems: "center"
            }}
          >
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'center',
              }}
            >
              <Avatar
                src=""
              />
            </Box>
            <Box sx={{ mt: 2 }}>
              <Typography
                align='center'
                color='textPrimary'
                variant='h3'
              >
                Asset created!
              </Typography>
            </Box>
            <Box sx={{ mt: 2 }}>
              <Typography
                align='center'
                color='textSecondary'
                variant='subtitle1'
              >
                The asset is now accessible for this task.
              </Typography>
            </Box>
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'center',
                mt: 2,
              }}
            >
              <Button
                color='primary'
                variant='contained'
                href={`${basepath}/assets/${created._id}/gui`}
              >
                Open asset
              </Button>
            </Box>
          </Box>)
          :
          file ? (
            <React.Fragment>
              <iframe key={iframeKey} style={{ width: "100%", minHeight: "80vh", border: 0 }} src={`https://docs.google.com/gview?url=${file.webContentLink}&embedded=true`} />
              <Button variant="outlined" fullWidth sx={{ mt: 1 }} onClick={() => setIframeKey(iframeKey + 1)}>Refresh previewer</Button>
              <Button variant="contained" fullWidth sx={{ mt: 2 }} onClick={confirmFile}>Confirm upload</Button>
            </React.Fragment>
          ) : <Box>
            <label htmlFor="contained-button-file">
              <Input id="contained-button-file" type="file" sx={{ display: "none" }} onChange={selectFile} />
              <Box
                sx={{
                  alignItems: 'center',
                  border: 1,
                  borderRadius: 1,
                  borderColor: 'divider',
                  display: 'flex',
                  flexWrap: 'wrap',
                  justifyContent: 'center',
                  outline: 'none',
                  p: 6,
                  '&:hover': {
                    backgroundColor: 'action.hover',
                    cursor: 'pointer',
                    opacity: 0.5,
                  },
                }}
              >
                <Box
                  sx={{
                    '& img': {
                      width: 100,
                    },
                  }}
                >
                  <img
                    alt='Select file'
                    src={`${basepath}/static/icon.svg`}
                  />
                </Box>
                <Box sx={{ p: 2 }}>
                  <Typography
                    color='textPrimary'
                    variant='h6'
                  >
                    {`Select file`}
                  </Typography>
                  <Box sx={{ mt: 2 }}>
                    <Typography
                      color='textPrimary'
                      variant='body1'
                    >
                      {`Drop file${maxFiles && maxFiles === 1 ? '' : 's'}`} or click here
                    </Typography>


                  </Box>
                </Box>
              </Box>
            </label>
            {progress !== 0 && <LinearProgress color="primary" variant="determinate" value={progress} />}
          </Box>
        }

      </div>
    </Container>
  );
}

ReactDOM.render(
  <ThemeProvider theme={theme}>
    {/* CssBaseline kickstart an elegant, consistent, and simple baseline to build upon. */}
    <CssBaseline />
    <App />
  </ThemeProvider>,
  document.querySelector('#root'),
);