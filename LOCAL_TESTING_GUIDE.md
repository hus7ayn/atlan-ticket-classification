# 🧪 Local Testing Guide - Atlan Ticket Classification System

## ✅ App Status: RUNNING SUCCESSFULLY

**URL**: http://localhost:8501  
**Status**: ✅ Active and responding  
**Process**: Running in background  

## 🧪 Testing Checklist

### 1. **Basic App Loading** ✅
- [x] App loads without errors
- [x] Navigation sidebar appears
- [x] Two main pages visible:
  - 📊 Classification Report
  - 💬 Interactive Query

### 2. **Classification Report Page Testing**

#### **Step 1: Load Classification Report**
1. Go to **📊 Classification Report** tab
2. Click **"🔄 Load Classification Report"** button
3. **Expected**: 
   - Progress spinner appears
   - "Classifying tickets..." message
   - Real-time processing of 30 tickets
   - Success message: "✅ Classification completed successfully!"

#### **Step 2: Verify Statistics Dashboard**
1. **Expected Metrics**:
   - Total Tickets: 30
   - Successful: 30
   - Failed: 0
   - Success Rate: 100.0%

2. **Expected Charts**:
   - **Topic Distribution**: Pie chart showing topics
   - **Sentiment Distribution**: Bar chart showing sentiments
   - **Priority Distribution**: Bar chart showing priorities

#### **Step 3: Test Ticket Details**
1. **Expected**: Expandable ticket cards
2. **Click on any ticket** to expand
3. **Verify Content**:
   - ✅ Ticket ID (e.g., TICKET-245)
   - ✅ Subject line
   - ✅ Full body text (scrollable)
   - ✅ Classification: Topic, Sentiment, Priority
   - ✅ AI Reasoning for each classification

#### **Step 4: Test Filtering**
1. **Topic Filter**: Select different topics (API/SDK, Connector, etc.)
2. **Sentiment Filter**: Select different sentiments (Curious, Frustrated, etc.)
3. **Priority Filter**: Select different priorities (P0, P1, P2)
4. **Expected**: Ticket list updates dynamically

### 3. **Interactive Query Page Testing**

#### **Step 1: Test Basic Query**
1. Go to **💬 Interactive Query** tab
2. Enter query: `"How to connect Snowflake to Atlan?"`
3. Click **"🔍 Process Query"**
4. **Expected**:
   - Processing spinner
   - Classification results (Topic, Sentiment, Priority)
   - Response (either Tavily answer or routing message)
   - Source URLs (if applicable)

#### **Step 2: Test Different Query Types**

**API/SDK Query** (Should get Tavily answer):
```
"What are the API authentication methods?"
```
**Expected**: 
- Topic: API/SDK
- Tavily-generated answer with sources
- Clickable source links

**Connector Query** (Should get routing):
```
"My connector is failing to crawl data"
```
**Expected**:
- Topic: Connector
- Routing message to appropriate team

**SSO Query** (Should get Tavily answer):
```
"How to set up SSO with Okta?"
```
**Expected**:
- Topic: SSO
- Tavily-generated answer with sources

#### **Step 3: Test Error Handling**
1. **Empty Query**: Click process without entering text
   - **Expected**: Warning message "Please enter a question."

2. **Invalid Query**: Enter random characters
   - **Expected**: Graceful error handling

### 4. **Performance Testing**

#### **Load Time Testing**:
- **Classification Report**: Should complete in 2-3 minutes
- **Query Processing**: Should complete in 3-5 seconds
- **Page Navigation**: Should be instant

#### **Memory Usage**:
- **Expected**: ~200-300MB RAM usage
- **Monitor**: Check Activity Monitor (macOS) or Task Manager

### 5. **UI/UX Testing**

#### **Responsive Design**:
1. **Desktop**: Full layout with sidebar
2. **Mobile**: Test on mobile browser
3. **Tablet**: Test on tablet browser

#### **Visual Elements**:
- [x] Clean, professional design
- [x] Proper color scheme
- [x] Readable fonts
- [x] Interactive charts
- [x] Smooth animations

### 6. **Data Integrity Testing**

#### **Verify Data Accuracy**:
1. **Ticket Count**: Should show exactly 30 tickets
2. **Classification Accuracy**: Check a few tickets manually
3. **Statistics**: Verify percentages add up to 100%
4. **Source Links**: Verify Tavily sources are valid URLs

## 🐛 Common Issues & Solutions

### **Issue 1: App Won't Start**
```bash
# Solution: Check dependencies
source venv/bin/activate
pip install -r requirements.txt
python run_streamlit.py
```

### **Issue 2: API Errors**
- **Grok API**: Check API key in config.py
- **Tavily API**: Check API key in config.py
- **Network**: Check internet connection

### **Issue 3: Slow Performance**
- **Memory**: Close other applications
- **Network**: Check API response times
- **Caching**: Clear browser cache

### **Issue 4: Charts Not Loading**
- **Dependencies**: Ensure plotly is installed
- **Browser**: Try different browser
- **JavaScript**: Enable JavaScript in browser

## 📊 Expected Test Results

### **Classification Report**:
- ✅ 30 tickets processed successfully
- ✅ 100% success rate
- ✅ Interactive charts working
- ✅ Filtering functional
- ✅ Ticket details expandable

### **Interactive Query**:
- ✅ API/SDK queries get Tavily answers
- ✅ Other queries get routing messages
- ✅ Source links clickable
- ✅ Error handling working
- ✅ Response summarization working

## 🚀 Ready for Deployment?

**If all tests pass**, your app is ready for Streamlit Cloud deployment!

**Next Steps**:
1. ✅ Local testing complete
2. 🔄 Deploy to GitHub
3. 🌐 Deploy to Streamlit Cloud
4. 🔑 Set environment variables
5. 🎉 Share your app!

## 📞 Support

If you encounter any issues during testing:
1. Check the terminal output for errors
2. Verify all dependencies are installed
3. Check API keys are correct
4. Try refreshing the browser
5. Restart the application

**Happy Testing!** 🧪✨
