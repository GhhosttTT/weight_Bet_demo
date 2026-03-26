const express = require('express');
const bodyParser = require('body-parser');
const app = express();
const port = process.env.PORT || 3000;
app.use(bodyParser.json());

// Mock GET /me/pending-actions
app.get('/api/me/pending-actions', (req, res) => {
  res.json({
    success: true,
    data: {
      invitations: [
        { id: 'inv123', planId: 'plan_1', fromUserId: 'user_a', message: '邀请你参与减肥对赌', type: 'invite', isFirstTime: true }
      ],
      doubleChecks: [
        { planId: 'plan_1', initiatorId: 'user_b', reason: 'participant_submitted_goal', isPending: true }
      ]
    }
  });
});

// Mock POST /invitations/:id/mark-seen
app.post('/api/invitations/:id/mark-seen', (req, res) => {
  console.log('Mark-seen called for', req.params.id, 'body:', req.body);
  res.json({ success: true });
});

// Mock POST /betting-plans/:id/doublecheck
app.post('/api/betting-plans/:id/doublecheck', (req, res) => {
  console.log('Doublecheck called for', req.params.id, 'body:', req.body);
  res.json({ success: true });
});

app.listen(port, () => {
  console.log(`Mock server listening on port ${port}`);
});

