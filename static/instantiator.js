const {
  colors,
  CssBaseline,
  ThemeProvider,
  Typography,
  Container,
  createTheme,
  Box,
  Button,
  Input,
  SvgIcon,
  Link,
  LinearProgress
} = MaterialUI;


const http = axios.create({
  headers: {
    "Content-type": "application/json"
  }
});

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

  getFiles() {
    return http.get("/files");
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

  var onUploadProgress = (progressEvent) => {
    setProgress(100 * progressEvent.loaded / progressEvent.total)
  }

  const selectFile = async (event) => {
    var file = event.target.files[0]
    uploadService.upload(file, onUploadProgress).then(response => {
      console.log("RESPONSE", response.data);
      if (window.parent) {
        window.parent.postMessage({
          'code': 'asset_created',
          'message': response.data
        }, "*");
      }
      setProgress(0)
    })
  }

  return (
    <Container maxWidth="sm">
      <Box sx={{ my: 4 }}>      <label htmlFor="contained-button-file">
        <Input id="contained-button-file" type="file" sx={{ display: "none" }} onChange={selectFile} />
        <Button variant="contained" component="span" fullWidth >
          Upload
        </Button>
        {progress !== 0 && <LinearProgress color="secondary" variant="determinate" value={progress} />}
      </label>
      </Box>
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