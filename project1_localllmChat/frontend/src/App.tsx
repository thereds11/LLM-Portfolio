import { useState, useRef } from 'react'
import {
  Box,
  Button,
  Container,
  Heading,
  Select,
  Textarea,
  VStack,
  HStack,
  Text,
  createListCollection,
  Portal,
} from '@chakra-ui/react'

import './App.css'
type Message = {
  role: 'user' | 'assistant'
  content: string
};

export default function App() {
  const [model, setModel] = useState<string[]>(['llama3'])
  const [chat, setChat] = useState<Message[]>([])
  const [prompt, setPrompt] = useState('')
  const wsRef = useRef<WebSocket | null>(null)
  
  async function startWebsocket(messages: Message[]) {
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }

    const ws = new WebSocket((location.protocol === 'https:' ? 'wss://' : 'ws://') + `${location.hostname}:8000` + '/ws/chat')
    wsRef.current = ws

    ws.onopen = () => {
      console.log('ws open')
      console.log('ws send', { model, messages })
      ws.send(JSON.stringify({ model, messages }))
    }

    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data)
        if (msg.type === 'token') {
          setChat((c) => {
            const last = c[c.length - 1]
            if (last && last.role === 'assistant') {
              const updated = [...c.slice(0, -1), { ...last, content: last.content + msg.token }]
              return updated
            }
            return [...c, { role: 'assistant', content: msg.token }]
          })
        } else if (msg.type === 'done') {
          // append done info
        } else if (msg.type === 'error') {
          setChat((c) => [...c, { role: 'assistant', content: 'Error: ' + msg.message }])
        }
      } catch (e) {
        console.error('ws parse', e)
      }
    }

    ws.onclose = () => {
      wsRef.current = null
    }
  }

  function send() {
    const userMsg: Message = { role: 'user', content: prompt }
    const messages: Message[] = [...chat, userMsg]
    setChat(messages)
    setPrompt('')
    startWebsocket(messages)
  }

  function cancel() {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: 'cancel' }))
    }
  }
  const models = createListCollection({
    items: [
      { value: 'llama3', label: 'llama3' },
      { value: 'phi3', label: 'phi3' },
      { value: 'mistral', label: 'mistral' },
    ]
  });

  return (
    <Container fluid px={4} py={6}>
      <VStack
        // spacing={4} 
        align="stretch">
        <Heading size="md">Local LLM Chat (React + Chakra + WS)</Heading>
        <HStack
          alignItems={"end"}
        >
          <Select.Root
            collection={models}
            width={"320px"}
            value={model}
            onValueChange={(e) => setModel(e.value)}
          >
            <Select.HiddenSelect />
            <Select.Label>Select Model</Select.Label>
            <Select.Control>
              <Select.Trigger>
                <Select.ValueText placeholder='Select Model' />
              </Select.Trigger>
              <Select.IndicatorGroup>
                <Select.Indicator />
              </Select.IndicatorGroup>
            </Select.Control>
            <Portal>
              <Select.Positioner>
                <Select.Content>
                  {models.items.map((item) => (
                    <Select.Item key={item.label} item={item}>
                      <Select.ItemText>{item.label}</Select.ItemText>
                      <Select.ItemIndicator>
                        <Select.Indicator />
                      </Select.ItemIndicator>
                    </Select.Item>
                  ))}
                </Select.Content>
              </Select.Positioner>
            </Portal>
          </Select.Root>
          <Button colorScheme="red" onClick={cancel}>
            Cancel
          </Button>
        </HStack>

        <Box borderWidth="1px" borderRadius="md" p={3} height="300px" overflowY="auto">
          {chat.map((m, i) => (
            <Box key={i} mb={2}>
              <Text fontWeight="bold">{m.role}:</Text>
              <Text whiteSpace="pre-wrap">{m.content}</Text>
            </Box>
          ))}
        </Box>

        <Textarea value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder="Type your question..." />
        <HStack>
          <Button 
            onClick={send} 
            colorScheme="blue"
            disabled={!prompt.trim() || !model.length}
          >
            Send
          </Button>
        </HStack>
      </VStack>
    </Container>
  )
}
