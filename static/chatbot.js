document.addEventListener('DOMContentLoaded', () => {
  const chatbotMessages = document.getElementById('chatbot-messages');
  const chatbotInputField = document.getElementById('chatbot-input-field');
  const chatbotSend = document.getElementById('chatbot-send');
  let isSending = false;

  // Function to add a message to the chat
  function addMessage(role, message) {
      const messageDiv = document.createElement('div');
      messageDiv.classList.add('message', role);
      messageDiv.textContent = message;
      chatbotMessages.appendChild(messageDiv);
      chatbotMessages.scrollTop = chatbotMessages.scrollHeight; // Auto-scroll
  }

  // Show loading indicator
  function showLoadingIndicator() {
      const loadingDiv = document.createElement('div');
      loadingDiv.classList.add('message', 'ai', 'loading');
      loadingDiv.textContent = 'Typing...';
      chatbotMessages.appendChild(loadingDiv);
      chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
      return loadingDiv;
  }

  // Hide loading indicator
  function hideLoadingIndicator(loadingDiv) {
      loadingDiv.remove();
  }

  // Send message to the chatbot
  chatbotSend.addEventListener('click', async () => {
      if (isSending) return; // Prevent multiple requests

      const userMessage = chatbotInputField.value.trim();
      if (userMessage) {
          isSending = true;
          addMessage('user', userMessage);
          chatbotInputField.value = '';
          chatbotSend.disabled = true;

          const loadingDiv = showLoadingIndicator();

          try {
              const response = await fetch('/chatbot', {
                  method: 'POST',
                  headers: {
                      'Content-Type': 'application/json',
                  },
                  body: JSON.stringify({ message: userMessage }),
              });

              if (!response.ok) {
                  throw new Error(`Server responded with status ${response.status}`);
              }

              const data = await response.json();
              addMessage('ai', data.response);
          } catch (error) {
              console.error('Error:', error);
              addMessage('ai', 'Sorry, something went wrong. Please try again later.');
          } finally {
              hideLoadingIndicator(loadingDiv);
              chatbotSend.disabled = false;
              chatbotInputField.focus();
              isSending = false;
          }
      }
  });

  // Allow pressing Enter to send a message
  chatbotInputField.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
          chatbotSend.click();
      }
  });

  // Disable send button if input is empty
  chatbotInputField.addEventListener('input', () => {
      const userMessage = chatbotInputField.value.trim();
      chatbotSend.disabled = !userMessage;
  });
});