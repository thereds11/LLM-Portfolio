import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { ChakraProvider, defaultSystem } from '@chakra-ui/react'
import './index.css'
import App from './App.tsx'


createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ChakraProvider 
      value={defaultSystem}
    // {...({} as ChakraProviderProps)}
    >
      <App />
    </ChakraProvider>
  </StrictMode>,
)
