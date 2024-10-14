// src/IntentDetail.js

import React, { useState, useEffect } from 'react';
import { TextField, Button, Grid } from '@material-ui/core';

function IntentDetail({ intent, onBack }) {
  const [functionCalls, setFunctionCalls] = useState('');
  const [specPortions, setSpecPortions] = useState([]);

  useEffect(() => {
    fetch(`${process.env.REACT_APP_BACKEND_URL}/generate_for_intent`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ intent }),
    })
      .then(response => response.json())
      .then(data => {
        setFunctionCalls(JSON.stringify(data.function_calls, null, 2));
        setSpecPortions(data.spec_portions);
      });
  }, [intent]);

  const handleSave = () => {
    fetch(`${process.env.REACT_APP_BACKEND_URL}/persist_output`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        intent,
        corrected_function_calls: JSON.parse(functionCalls),
      }),
    }).then(response => response.json());
  };

  return (
    <div>
      <Button onClick={onBack}>Back to Intent List</Button>
      <h2>{intent}</h2>
      <Grid container spacing={3}>
        <Grid item xs={6}>
          <h3>Function Calls</h3>
          <TextField
            multiline
            fullWidth
            rows={20}
            variant="outlined"
            value={functionCalls}
            onChange={(e) => setFunctionCalls(e.target.value)}
          />
        </Grid>
        <Grid item xs={6}>
          <h3>Relevant API Spec Portions</h3>
          {/* <pre>{JSON.stringify(JSON.parse(specPortions.join('\n\n') || '{}'), null, 2)}</pre> */}
          <pre>{specPortions.join('\n\n')}</pre>
        </Grid>
      </Grid>
      <Button variant="contained" color="primary" onClick={handleSave}>
        Save
      </Button>
    </div>
  );
}

export default IntentDetail;
