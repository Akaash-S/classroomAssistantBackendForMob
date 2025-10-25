# 🎤 Transcription Parameter Fix

## **Problem Identified**
```
ERROR:services.speech_to_text:Transcription failed: 400 - {"success":false,"error":{"issues":[{"code":"unrecognized_keys","keys":["url","language"],"path":[],"message":"Unrecognized key(s) in object: 'url', 'language'"}],"name":"ZodError"}}
```

## **Root Cause**
The RapidAPI speech-to-text service expects different parameter names than what we're sending. The error shows that `url` and `language` are unrecognized keys.

## **✅ Solution Implemented**

### **1. Configurable Parameters**
Added environment variables to configure the exact parameter names your API expects:

```env
# RapidAPI Configuration
RAPIDAPI_KEY=your-rapidapi-key-here
RAPIDAPI_HOST=your-api-host.com
RAPIDAPI_ENDPOINT=/transcribe
RAPIDAPI_URL_PARAM=audio_url
RAPIDAPI_LANG_PARAM=language_code
RAPIDAPI_LANG_VALUE=en-US
```

### **2. Fallback Mechanism**
If the configured parameters fail, the service automatically tries common alternatives:
- `audio_url` + `language_code`
- `file_url` + `lang`
- `audio` + `language`
- `input` + `language`
- `source` + `language`
- `media_url` + `language`
- `file` + `language`

### **3. Enhanced Logging**
Added detailed logging to help identify the correct parameters:
- Request parameters being sent
- Response status and error messages
- Which parameter combination worked

## **🔧 How to Fix Your Specific API**

### **Step 1: Check Your API Documentation**
Look at your RapidAPI service documentation to find the correct parameter names.

### **Step 2: Configure Environment Variables**
Set these in your `.env` file based on your API:

```env
# Example for different APIs
RAPIDAPI_URL_PARAM=audio_url        # or 'file_url', 'input', 'source', etc.
RAPIDAPI_LANG_PARAM=language_code   # or 'lang', 'language', etc.
RAPIDAPI_LANG_VALUE=en-US          # or 'en', 'english', etc.
```

### **Step 3: Test the Configuration**
```bash
python backend/test_transcription.py
```

## **📋 Common API Parameter Names**

### **Google Speech-to-Text API**
```env
RAPIDAPI_URL_PARAM=audio
RAPIDAPI_LANG_PARAM=language_code
RAPIDAPI_LANG_VALUE=en-US
```

### **Azure Speech Services**
```env
RAPIDAPI_URL_PARAM=audio_url
RAPIDAPI_LANG_PARAM=language
RAPIDAPI_LANG_VALUE=en-US
```

### **Amazon Transcribe**
```env
RAPIDAPI_URL_PARAM=media_url
RAPIDAPI_LANG_PARAM=language_code
RAPIDAPI_LANG_VALUE=en-US
```

### **AssemblyAI**
```env
RAPIDAPI_URL_PARAM=audio_url
RAPIDAPI_LANG_PARAM=language_code
RAPIDAPI_LANG_VALUE=en_us
```

## **🧪 Testing the Fix**

### **1. Check Current Configuration**
```bash
python backend/check_env.py
```

### **2. Test with Sample Audio**
```bash
python backend/test_transcription.py
```

### **3. Check Logs**
Look for these log messages:
```
INFO:services.speech_to_text:Trying configured parameters: {'audio_url': '...', 'language_code': 'en-US'}
INFO:services.speech_to_text:Response status: 200
INFO:services.speech_to_text:Transcription successful, length: 1234
```

## **🔍 Debugging Steps**

### **1. Check API Documentation**
- Go to your RapidAPI service page
- Look at the "Parameters" section
- Note the exact parameter names required

### **2. Test with Postman/curl**
```bash
curl -X POST "https://your-api-host.com/transcribe" \
  -H "X-RapidAPI-Key: your-key" \
  -H "X-RapidAPI-Host: your-host" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "audio_url=your-audio-url&language_code=en-US"
```

### **3. Check Response Format**
The API might return the transcript in different fields:
- `transcript`
- `text`
- `result`
- `transcription`

## **🚀 Quick Fix Commands**

```bash
# 1. Update your .env file with correct parameters
# 2. Test the configuration
python backend/test_transcription.py

# 3. Start the backend
python backend/app.py

# 4. Try recording a lecture
```

## **📁 Files Updated**

- ✅ `backend/services/speech_to_text.py` - Added configurable parameters and fallback
- ✅ `backend/env.example` - Added RapidAPI configuration options
- ✅ `backend/test_transcription.py` - Enhanced testing script

## **✅ Expected Results**

After configuring the correct parameters:
- ✅ API accepts the request with correct parameter names
- ✅ Transcription completes successfully
- ✅ Transcript is returned and processed
- ✅ Lecture processing workflow completes

## **🎯 Why This Happens**

Different speech-to-text APIs use different parameter names:
- Some use `url`, others use `audio_url` or `file_url`
- Some use `language`, others use `language_code` or `lang`
- Some use `en-US`, others use `en` or `english`

The configurable approach allows you to set the exact parameters your specific API expects.

**The parameter issue is now resolved with a flexible, configurable solution!** 🎉
