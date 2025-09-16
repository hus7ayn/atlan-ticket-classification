# 🚀 Streamlit Deployment Guide

## Deployment Options

### Option 1: Streamlit Cloud (Recommended - Free)

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Atlan Ticket Classification System"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/atlan-ticket-classification.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository: `atlan-ticket-classification`
   - Main file path: `streamlit_app.py`
   - Click "Deploy!"

### Option 2: Heroku

1. **Install Heroku CLI**:
   ```bash
   # macOS
   brew install heroku/brew/heroku
   
   # Or download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Deploy**:
   ```bash
   heroku login
   heroku create atlan-ticket-classification
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

### Option 3: Railway

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Deploy**:
   ```bash
   railway login
   railway init
   railway up
   ```

### Option 4: Render

1. **Connect GitHub repository**
2. **Create new Web Service**
3. **Configure**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0`

## Environment Variables

For production deployment, set these environment variables:

```bash
GROK_API_KEY=your_grok_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
GROK_MODEL=gemma2-9b-it
```

## Local Testing

Test your deployment locally:

```bash
# Test with production settings
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0

# Or use the startup script
python run_streamlit.py
```

## Troubleshooting

### Common Issues:

1. **Import Errors**: Ensure all dependencies are in `requirements.txt`
2. **Port Issues**: Use `$PORT` environment variable for cloud deployment
3. **API Keys**: Set environment variables in your deployment platform
4. **Memory Issues**: Consider upgrading to a paid plan for large datasets

### File Structure for Deployment:

```
atlan-ticket-classification/
├── streamlit_app.py          # Main app
├── run_streamlit.py          # Startup script
├── requirements.txt          # Dependencies
├── Procfile                  # Heroku/Railway config
├── runtime.txt              # Python version
├── .streamlit/
│   └── config.toml          # Streamlit config
├── utils.py                 # Shared utilities
├── config.py                # Configuration
├── ticket_classifier.py     # Classification logic
├── smart_ticket_processor.py # Smart processing
├── tavily_client.py         # Tavily integration
├── ticket_api.py            # API layer
├── grok_client.py           # Grok client
├── process_all_tickets.py   # CLI processing
├── add_ticket.py            # Add tickets
├── tickets_data.json        # Ticket data
└── README.md                # Documentation
```

## Security Notes

- Never commit API keys to version control
- Use environment variables for sensitive data
- Consider rate limiting for public deployments
- Monitor usage and costs

## Performance Optimization

- Use `@st.cache_data` for expensive operations
- Implement pagination for large datasets
- Consider database storage for production
- Monitor memory usage

## Support

If you encounter issues:
1. Check the deployment platform logs
2. Test locally first
3. Verify all dependencies are installed
4. Check environment variables are set correctly
