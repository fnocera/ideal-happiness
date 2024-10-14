// src/App.js

import React, { useState, useEffect } from 'react';
import IntentList from './IntentList';
import IntentDetail from './IntentDetail';
import { Container } from '@material-ui/core';

function App() {
  const [intents, setIntents] = useState([]);
  const [selectedIntent, setSelectedIntent] = useState(null);

  useEffect(() => {
    fetch(`${process.env.REACT_APP_BACKEND_URL}/intents`)
      .then(response => response.json())
      .then(data => setIntents(data.intents));
  }, []);

  const handleIntentClick = (intent) => {
    setSelectedIntent(intent);
  };

  return (
    <Container>
      {!selectedIntent ? (
        <IntentList intents={intents} onIntentClick={handleIntentClick} />
      ) : (
        <IntentDetail intent={selectedIntent} onBack={() => setSelectedIntent(null)} />
      )}
    </Container>
  );
}

export default App;
