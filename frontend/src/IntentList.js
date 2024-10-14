// src/IntentList.js

import React from 'react';
import { List, ListItem, ListItemText, Button } from '@material-ui/core';

function IntentList({ intents, onIntentClick }) {
    const handleFileUpload = async (event) => {
        const file = event.target.files[0];
        const formData = new FormData();
        formData.append('file', file);
      
        await fetch(`${process.env.REACT_APP_BACKEND_URL}/upload_intents`, {
          method: 'POST',
          body: formData,
        });
      
        // Refresh intents list
        fetch(`${process.env.REACT_APP_BACKEND_URL}/intents`)
          .then(response => response.json())
          .then(data => setIntents(data.intents));
      };

  return (
    <div>
      <h2>User Intents</h2>
      <input
        accept=".txt"
        style={{ display: 'none' }}
        id="upload-intents"
        type="file"
        onChange={handleFileUpload}
      />
      <label htmlFor="upload-intents">
        <Button variant="contained" color="primary" component="span">
          Upload Intents File
        </Button>
      </label>
      <List>
        {intents.map((intent, index) => (
          <ListItem button key={index} onClick={() => onIntentClick(intent)}>
            <ListItemText primary={intent} />
          </ListItem>
        ))}
      </List>
    </div>
  );
}

export default IntentList;
