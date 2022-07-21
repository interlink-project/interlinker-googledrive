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
  Avatar,
  Grid,
  Select,
  MenuItem,
  TextField,
  Stack
} = MaterialUI;

var { domain, basepath, datafrombackend } = jQuery('#data').data();
const origin = domain.PROTOCOL + domain.SERVER_NAME

const http = axios.create({
  headers: {
    "Content-type": "application/json"
  }
});

class Service {
  setAdditionalEmails(data) {
    return http.post(`${basepath}/api/v1/setAdditionalEmails`, data);
  }
}

const service = new Service();

const validateEmail = (email) => {
  return String(email)
    .toLowerCase()
    .match(
      /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
    );
};

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
  const [emails, setEmails] = React.useState(datafrombackend.config.additionalEmails || [])
  const [loading, setLoading] = React.useState(false);


  const submit = () => {
    if(emails.map(el => el !== "" && el) !== datafrombackend.config.additionalEmails ){
      setLoading(true)
      console.log(emails)
      service.setAdditionalEmails(emails)
        .then(response => {
          window.location.replace(datafrombackend.redirectUrl);
        })
        .finally(() => setLoading(false))
    }else{
      window.location.replace(datafrombackend.redirectUrl);
    }
    
  }



  return (
    <Container maxWidth="lg">
      <Stack justifyContent="center">
        Your primary emails:
        <TextField sx={{mt: 1, mb: 2}} disabled value={datafrombackend.user && datafrombackend.user.email} variant="outlined" />

        Your additional emails:
        {emails.map((email, i) => <TextField key={"email" + i.toString()} id={"email" + i.toString()} error={!validateEmail(email)} value={email} onChange={(e) => {
          let cp = [...emails]
          cp[i] = e.target.value
          setEmails(cp)
        }} />)}
        <Button disabled={loading || (emails.length > 0 && !emails.every(validateEmail))} variant="contained" sx={{ mt: 2 }} onClick={() => setEmails([...emails, ""])}>
          Add new email
        </Button>
      </Stack>
      <Button disabled={loading} fullWidth variant="contained" sx={{ mt: 2 }} onClick={() => submit()}>
        Continue
      </Button>
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