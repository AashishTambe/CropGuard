"""
CropGuard internationalization.

Supported languages:
    en = English
    mr = Marathi
    hi = Hindi

Technical pesticide and agricultural terminology is kept
conservative and should not be interpreted as a replacement
for locally approved agricultural recommendations.
"""

from __future__ import annotations


# =========================================================
# SUPPORTED LANGUAGES
# =========================================================

LANGS = {
    "en": "English",
    "mr": "मराठी",
    "hi": "हिन्दी",
}


# =========================================================
# UI STRINGS
# =========================================================

STRINGS = {

    # =====================================================
    # ENGLISH
    # =====================================================
    "en": {

        # -------------------------------------------------
        # Existing application strings
        # -------------------------------------------------
        "app_name": "CropGuard AI",
        "subtitle": "AI-powered Early Crop Disease & Pest Surveillance System",
        "tagline": "Early detection. Smarter intervention. Healthier crops.",

        "nav_home": "Home",
        "nav_farmer": "Farmer Detection",
        "nav_risk": "Risk Analysis",
        "nav_expert": "Expert Review",
        "nav_dashboard": "Surveillance Dashboard",
        "nav_followup": "Follow-up",
        "nav_about": "About",

        "demo_on": "Demo Mode: ON",
        "ai_ready": "AI Status",
        "weather_status": "Weather",
        "db_status": "Database",

        "connected": "Connected",
        "demo": "Demo",
        "ready": "Ready",

        "disclaimer": (
            "This prototype provides decision support and does not replace "
            "diagnosis by qualified agricultural experts or laboratories. "
            "Always follow locally approved agricultural recommendations "
            "and product labels."
        ),

        "select_crop": "Select crop",
        "select_variety": "Select variety",
        "growth_stage": "Crop growth stage",

        "location": "Location",
        "village": "Village",
        "district": "District",
        "state": "State",

        "latitude": "Latitude",
        "longitude": "Longitude",

        "soil_type": "Soil type",
        "soil_moisture": "Soil moisture",
        "soil_ph": "Soil pH",
        "drainage": "Drainage",

        "upload_image": "Upload leaf / plant / pest image (JPG or PNG)",
        "analyze": "Analyze crop image",

        "diagnosis": "What might already be affecting this plant?",
        "risk_meaning": (
            "How likely is this issue to become a problem under current conditions?"
        ),

        "likely_issue": "Likely issue",
        "confidence": "AI Confidence",
        "risk": "Outbreak risk",
        "why": "Why this risk?",
        "advisory": "IPM advisory",

        "submit_case": "Submit Case",
        "request_expert": "Request Expert Verification",
        "monitor_again": "Monitor Again",
        "read_aloud": "Read advisory aloud",

        "low_conf": (
            "Possible issue detected. Expert verification recommended."
        ),

        "not_definitive": "This is not a definitive diagnosis.",

        "demo_pred": (
            "Demo prediction — replace with trained/open model for production."
        ),

        "demo_weather": (
            "Weather service unavailable. Showing demo weather data."
        ),

        "prototype_risk": (
            "Prototype risk model — requires local agronomic calibration."
        ),

        "lab_needed": "Laboratory verification recommended.",

        "generate_referral": "Generate Referral",
        "confirm": "Confirm",
        "reject": "Reject",
        "needs_lab": "Needs lab test",

        "immediate": "Immediate action",
        "monitoring": "Monitoring",
        "cultural": "Cultural / mechanical",
        "biological": "Biological",
        "chemical": "Chemical (only if justified)",
        "safety": "Safety",
        "escalation": "When to contact officer",

        "hotspot": "Potential hotspot",

        "simulated": (
            "SIMULATED DEMO DATA — NOT REAL GOVERNMENT SURVEILLANCE DATA"
        ),

        "case_saved": (
            "Case saved. It now appears on the surveillance map."
        ),

        "expert_confirmed": "Expert Confirmed",
        "followup_saved": "Follow-up record saved.",

        "poor_image": (
            "Image quality is low. Please capture a clear image "
            "of the affected leaf/plant."
        ),

        "cap1": "AI Disease Detection",
        "cap2": "Weather Risk Forecasting",
        "cap3": "Outbreak Hotspot Mapping",
        "cap4": "IPM Advisory",

        "how": "How it works",
        "step1": "Capture",
        "step2": "Analyze",
        "step3": "Predict",
        "step4": "Act",
        "step5": "Monitor",

        # -------------------------------------------------
        # Dashboard strings
        # -------------------------------------------------
        "smart_crop_protection": "SMART CROP PROTECTION",

        "good_morning": "Good Morning",
        "good_afternoon": "Good Afternoon",
        "good_evening": "Good Evening",
        "good_night": "Good Night",

        "farm_hero": "Farm Hero",

        "hero_description": (
            "See your crop health at a glance and scan a leaf "
            "when something looks different."
        ),

        "farm_conditions": "Your farm conditions",

        "nashik_maharashtra": "Nashik, Maharashtra",

        "demo_location": "Approximate demo location",

        "updated_at": "updated",

        "temperature": "Temperature",
        "humidity": "Humidity",
        "wind": "Wind",
        "rainfall": "Rainfall",

        "weather_source": "Open-Meteo / demo fallback",

        "next_best_action": "NEXT BEST ACTION",

        "scan_your_crop": "Scan your crop",

        "scan_description": (
            "Capture a clear leaf photo for an AI screening "
            "and weather-aware guidance."
        ),

        "start_crop_scan": "Start a crop scan",

        "crop_health_overview": "Crop health overview",

        "overall_crop_health": "Overall crop health",
        "based_on_saved_scans": "Based on saved scans",

        "total_scans": "Total scans",
        "ai_screenings_recorded": "AI screenings recorded",

        "healthy": "Healthy",
        "continue_monitoring": "Continue monitoring",

        "issues_detected": "Issues detected",
        "review_recommendations": "Review recommendations",

        "recent_scans": "Recent scans",

        "recent_scans_empty": (
            "Your recent scans will appear here."
        ),

        "confidence_short": "confidence",

        "weather_risk_insight": "Weather risk insight",

        "weather_risk_high": (
            "Humid or wet conditions can increase pressure from some "
            "fungal diseases. Improve airflow and avoid unnecessary "
            "leaf wetness."
        ),

        "weather_risk_low": (
            "Current conditions are favorable for leaves to dry. "
            "Continue regular crop checks."
        ),

        "risk_disclaimer": (
            "This is an informational crop-risk signal, not a diagnosis."
        ),

        "how_cropguard_works": "How CropGuard works",

        "step_find_farm": "Find your farm",
        "step_find_farm_body": (
            "Use the location and weather context."
        ),

        "step_capture_leaf": "Capture a leaf",
        "step_capture_leaf_body": (
            "Use the camera or choose a photo."
        ),

        "step_next_step": "Take the next step",
        "step_next_step_body": (
            "Review confidence, risk and IPM guidance."
        ),

        "footer_disclaimer": (
            "CropGuard is decision support. Confirm uncertain cases "
            "with a qualified agricultural expert or laboratory."
        ),
    },


    # =====================================================
    # HINDI
    # =====================================================
    "hi": {

        # -------------------------------------------------
        # Existing application strings
        # -------------------------------------------------
        "app_name": "CropGuard AI",

        "subtitle": (
            "फसल रोग और कीट निगरानी प्रणाली"
        ),

        "tagline": (
            "जल्दी पहचान। समझदार उपाय। स्वस्थ फसल।"
        ),

        "nav_home": "होम",
        "nav_farmer": "किसान जाँच",
        "nav_risk": "जोखिम विश्लेषण",
        "nav_expert": "विशेषज्ञ समीक्षा",
        "nav_dashboard": "निगरानी डैशबोर्ड",
        "nav_followup": "फॉलो-अप",
        "nav_about": "परिचय",

        "demo_on": "डेमो मोड: चालू",
        "ai_ready": "एआई स्थिति",
        "weather_status": "मौसम",
        "db_status": "डेटाबेस",

        "connected": "जुड़ा",
        "demo": "डेमो",
        "ready": "तैयार",

        "disclaimer": (
            "यह प्रोटोटाइप केवल निर्णय सहायता है। "
            "यह योग्य कृषि विशेषज्ञ या प्रयोगशाला की जगह नहीं लेता। "
            "केवल स्थानीय स्वीकृत सलाह और उत्पाद लेबल का पालन करें।"
        ),

        "select_crop": "फसल चुनें",
        "select_variety": "किस्म चुनें",
        "growth_stage": "फसल अवस्था",

        "location": "स्थान",
        "village": "गाँव",
        "district": "जिला",
        "state": "राज्य",

        "latitude": "अक्षांश",
        "longitude": "देशांतर",

        "soil_type": "मिट्टी का प्रकार",
        "soil_moisture": "मिट्टी की नमी",
        "soil_ph": "मिट्टी pH",
        "drainage": "जल निकास",

        "upload_image": (
            "पत्ती / पौधे / कीट की तस्वीर (JPG या PNG)"
        ),

        "analyze": "फसल तस्वीर जाँचें",

        "diagnosis": (
            "इस पौधे को अभी क्या प्रभावित कर सकता है?"
        ),

        "risk_meaning": (
            "मौजूदा हालात में यह समस्या कितनी बढ़ सकती है?"
        ),

        "likely_issue": "संभावित समस्या",
        "confidence": "एआई विश्वास",
        "risk": "प्रकोप जोखिम",
        "why": "जोखिम क्यों?",
        "advisory": "आईपीएम सलाह",

        "submit_case": "केस जमा करें",
        "request_expert": "विशेषज्ञ जाँच माँगें",
        "monitor_again": "फिर निगरानी करें",
        "read_aloud": "सलाह सुनें",

        "low_conf": (
            "संभावित समस्या दिखी है। "
            "विशेषज्ञ पुष्टि सुझाई जाती है।"
        ),

        "not_definitive": "यह अंतिम निदान नहीं है।",

        "demo_pred": (
            "डेमो पूर्वानुमान — उत्पादन में प्रशिक्षित/ओपन मॉडल लगाएँ।"
        ),

        "demo_weather": (
            "मौसम सेवा उपलब्ध नहीं। डेमो मौसम दिखाया जा रहा है।"
        ),

        "prototype_risk": (
            "प्रोटोटाइप जोखिम मॉडल — स्थानीय कृषि सत्यापन आवश्यक है।"
        ),

        "lab_needed": "प्रयोगशाला पुष्टि सुझाई जाती है।",

        "generate_referral": "रेफरल बनाएँ",
        "confirm": "पुष्टि",
        "reject": "अस्वीकार",
        "needs_lab": "लैब परीक्षण चाहिए",

        "immediate": "तुरंत करें",
        "monitoring": "निगरानी",
        "cultural": "कृषि / यांत्रिक उपाय",
        "biological": "जैविक नियंत्रण",
        "chemical": "रसायन (केवल ज़रूरत पर)",
        "safety": "सुरक्षा",
        "escalation": "अधिकारी से कब संपर्क करें",

        "hotspot": "संभावित हॉटस्पॉट",

        "simulated": (
            "सिमुलेटेड डेमो डेटा — वास्तविक सरकारी निगरानी डेटा नहीं"
        ),

        "case_saved": (
            "केस सहेजा गया। यह अब निगरानी मानचित्र पर दिखेगा।"
        ),

        "expert_confirmed": "विशेषज्ञ पुष्टि",
        "followup_saved": "फॉलो-अप सहेजा गया।",

        "poor_image": (
            "तस्वीर की गुणवत्ता कम है। "
            "प्रभावित पत्ती/पौधे की साफ़ तस्वीर लें।"
        ),

        "cap1": "एआई रोग पहचान",
        "cap2": "मौसम आधारित जोखिम",
        "cap3": "प्रकोप मानचित्र",
        "cap4": "आईपीएम सलाह",

        "how": "कैसे काम करता है",
        "step1": "फोटो",
        "step2": "विश्लेषण",
        "step3": "पूर्वानुमान",
        "step4": "कार्रवाई",
        "step5": "निगरानी",

        # -------------------------------------------------
        # Dashboard strings
        # -------------------------------------------------
        "smart_crop_protection": "स्मार्ट फसल सुरक्षा",

        "good_morning": "सुप्रभात",
        "good_afternoon": "नमस्कार",
        "good_evening": "शुभ संध्या",
        "good_night": "शुभ रात्रि",

        "farm_hero": "किसान साथी",

        "hero_description": (
            "अपनी फसल के स्वास्थ्य को एक नज़र में देखें "
            "और कुछ अलग दिखाई देने पर पत्ती की जाँच करें।"
        ),

        "farm_conditions": "आपके खेत की स्थिति",

        "nashik_maharashtra": "नासिक, महाराष्ट्र",

        "demo_location": "अनुमानित डेमो स्थान",

        "updated_at": "अपडेट किया गया",

        "temperature": "तापमान",
        "humidity": "नमी",
        "wind": "हवा",
        "rainfall": "वर्षा",

        "weather_source": "Open-Meteo / डेमो डेटा",

        "next_best_action": "अगला सबसे अच्छा कदम",

        "scan_your_crop": "अपनी फसल की जाँच करें",

        "scan_description": (
            "एआई जाँच और मौसम आधारित मार्गदर्शन के लिए "
            "पत्ती की स्पष्ट तस्वीर लें।"
        ),

        "start_crop_scan": "फसल की जाँच शुरू करें",

        "crop_health_overview": "फसल स्वास्थ्य का अवलोकन",

        "overall_crop_health": "कुल फसल स्वास्थ्य",
        "based_on_saved_scans": "सहेजी गई जाँच के आधार पर",

        "total_scans": "कुल जाँच",
        "ai_screenings_recorded": "दर्ज की गई एआई जाँच",

        "healthy": "स्वस्थ",
        "continue_monitoring": "निगरानी जारी रखें",

        "issues_detected": "पाई गई समस्याएँ",
        "review_recommendations": "सिफारिशें देखें",

        "recent_scans": "हाल की जाँच",

        "recent_scans_empty": (
            "आपकी हाल की जाँच यहाँ दिखाई देंगी।"
        ),

        "confidence_short": "विश्वास",

        "weather_risk_insight": "मौसम जोखिम जानकारी",

        "weather_risk_high": (
            "नमी या गीली परिस्थितियाँ कुछ फफूंद रोगों का खतरा बढ़ा सकती हैं। "
            "हवा का प्रवाह बेहतर रखें और पत्तियों को अनावश्यक रूप से गीला न रखें।"
        ),

        "weather_risk_low": (
            "वर्तमान परिस्थितियाँ पत्तियों के सूखने के लिए अनुकूल हैं। "
            "फसल की नियमित जाँच जारी रखें।"
        ),

        "risk_disclaimer": (
            "यह केवल फसल जोखिम संबंधी जानकारी है, अंतिम निदान नहीं।"
        ),

        "how_cropguard_works": "CropGuard कैसे काम करता है",

        "step_find_farm": "अपना खेत खोजें",
        "step_find_farm_body": (
            "स्थान और मौसम की जानकारी का उपयोग करें।"
        ),

        "step_capture_leaf": "पत्ती की तस्वीर लें",
        "step_capture_leaf_body": (
            "कैमरे का उपयोग करें या फोटो चुनें।"
        ),

        "step_next_step": "अगला कदम उठाएँ",
        "step_next_step_body": (
            "विश्वास स्तर, जोखिम और आईपीएम मार्गदर्शन देखें।"
        ),

        "footer_disclaimer": (
            "CropGuard निर्णय सहायता प्रदान करता है। "
            "अनिश्चित मामलों की पुष्टि योग्य कृषि विशेषज्ञ "
            "या प्रयोगशाला से करें।"
        ),
    },


    # =====================================================
    # MARATHI
    # =====================================================
    "mr": {

        # -------------------------------------------------
        # Existing application strings
        # -------------------------------------------------
        "app_name": "CropGuard AI",

        "subtitle": (
            "पीक रोग व कीड पाळत ठेवणारी प्रणाली"
        ),

        "tagline": (
            "लवकर ओळख. योग्य उपाय. निरोगी पीक."
        ),

        "nav_home": "मुख्यपृष्ठ",
        "nav_farmer": "शेतकरी तपासणी",
        "nav_risk": "धोका विश्लेषण",
        "nav_expert": "तज्ज्ञ तपासणी",
        "nav_dashboard": "सर्व्हिलन्स डॅशबोर्ड",
        "nav_followup": "पाठपुरावा",
        "nav_about": "माहिती",

        "demo_on": "डेमो मोड: सुरू",
        "ai_ready": "एआय स्थिती",
        "weather_status": "हवामान",
        "db_status": "डेटाबेस",

        "connected": "जोडले",
        "demo": "डेमो",
        "ready": "तयार",

        "disclaimer": (
            "ही प्रणाली केवळ निर्णय सहाय्य देते. "
            "ती तज्ज्ञ किंवा प्रयोगशाळेची जागा घेत नाही. "
            "स्थानिक मान्यताप्राप्त शिफारशी व उत्पादनाच्या लेबलचे पालन करा."
        ),

        "select_crop": "पीक निवडा",
        "select_variety": "जात निवडा",
        "growth_stage": "पीक अवस्था",

        "location": "स्थान",
        "village": "गाव",
        "district": "जिल्हा",
        "state": "राज्य",

        "latitude": "अक्षांश",
        "longitude": "रेखांश",

        "soil_type": "मातीचा प्रकार",
        "soil_moisture": "ओलावा",
        "soil_ph": "माती pH",
        "drainage": "निचरा",

        "upload_image": (
            "पान / पीक / कीड याचा फोटो (JPG किंवा PNG)"
        ),

        "analyze": "पिकाचा फोटो तपासा",

        "diagnosis": (
            "या वनस्पतीवर आधीच काय परिणाम होत असू शकतो?"
        ),

        "risk_meaning": (
            "सध्याच्या परिस्थितीत ही समस्या किती वाढू शकते?"
        ),

        "likely_issue": "संभाव्य समस्या",
        "confidence": "एआय विश्वास",
        "risk": "प्रादुर्भाव धोका",
        "why": "धोका का?",
        "advisory": "आयपीएम सल्ला",

        "submit_case": "केस जमा करा",
        "request_expert": "तज्ज्ञ तपासणी मागा",
        "monitor_again": "पुन्हा निरीक्षण",
        "read_aloud": "सल्ला ऐका",

        "low_conf": (
            "संभाव्य समस्या दिसली. तज्ज्ञ खात्री सुचवली आहे."
        ),

        "not_definitive": "हे अंतिम निदान नाही.",

        "demo_pred": (
            "डेमो अंदाज — उत्पादनासाठी प्रशिक्षित/ओपन मॉडेल वापरा."
        ),

        "demo_weather": (
            "हवामान सेवा उपलब्ध नाही. डेमो हवामान दाखवत आहोत."
        ),

        "prototype_risk": (
            "प्रोटोटाइप धोका मॉडेल — स्थानिक कृषी समायोजन आवश्यक."
        ),

        "lab_needed": "प्रयोगशाळा तपासणी सुचवली आहे.",

        "generate_referral": "रेफरल तयार करा",
        "confirm": "खात्री",
        "reject": "नाकारा",
        "needs_lab": "लॅब टेस्ट हवी",

        "immediate": "ताबडतोब करा",
        "monitoring": "निरीक्षण",
        "cultural": "मशागत / यांत्रिक",
        "biological": "जैविक नियंत्रण",
        "chemical": "रासायनिक (फक्त गरज असल्यास)",
        "safety": "सुरक्षा",
        "escalation": "अधिकाऱ्यांशी केव्हा संपर्क करावा",

        "hotspot": "संभाव्य हॉटस्पॉट",

        "simulated": (
            "सिम्युलेटेड डेमो डेटा — वास्तविक शासकीय सर्व्हिलन्स डेटा नाही"
        ),

        "case_saved": (
            "केस जतन झाला. तो आता नकाशावर दिसेल."
        ),

        "expert_confirmed": "तज्ज्ञ खात्री",
        "followup_saved": "पाठपुरावा जतन झाला.",

        "poor_image": (
            "फोटोची गुणवत्ता कमी आहे. "
            "बाधित पान/वनस्पतीचा स्पष्ट फोटो घ्या."
        ),

        "cap1": "एआय रोग ओळख",
        "cap2": "हवामान धोका अंदाज",
        "cap3": "प्रादुर्भाव नकाशा",
        "cap4": "आयपीएम सल्ला",

        "how": "कसे कार्य करते",
        "step1": "फोटो",
        "step2": "विश्लेषण",
        "step3": "अंदाज",
        "step4": "कृती",
        "step5": "निरीक्षण",

        # -------------------------------------------------
        # Dashboard strings
        # -------------------------------------------------
        "smart_crop_protection": "स्मार्ट पीक संरक्षण",

        "good_morning": "शुभ सकाळ",
        "good_afternoon": "शुभ दुपार",
        "good_evening": "शुभ संध्याकाळ",
        "good_night": "शुभ रात्री",

        "farm_hero": "शेतकरी मित्र",

        "hero_description": (
            "तुमच्या पिकाचे आरोग्य एका नजरेत पहा "
            "आणि काही वेगळे दिसल्यास पानाची तपासणी करा."
        ),

        "farm_conditions": "तुमच्या शेताची स्थिती",

        "nashik_maharashtra": "नाशिक, महाराष्ट्र",

        "demo_location": "अंदाजे डेमो स्थान",

        "updated_at": "अपडेट केले",

        "temperature": "तापमान",
        "humidity": "आर्द्रता",
        "wind": "वारा",
        "rainfall": "पाऊस",

        "weather_source": "Open-Meteo / डेमो डेटा",

        "next_best_action": "पुढील योग्य कृती",

        "scan_your_crop": "तुमच्या पिकाची तपासणी करा",

        "scan_description": (
            "एआय तपासणी आणि हवामान आधारित मार्गदर्शनासाठी "
            "पानाचा स्पष्ट फोटो घ्या."
        ),

        "start_crop_scan": "पिकाची तपासणी सुरू करा",

        "crop_health_overview": "पिकाच्या आरोग्याचा आढावा",

        "overall_crop_health": "एकूण पिकाचे आरोग्य",
        "based_on_saved_scans": "साठवलेल्या तपासण्यांवर आधारित",

        "total_scans": "एकूण तपासण्या",
        "ai_screenings_recorded": "नोंद केलेल्या एआय तपासण्या",

        "healthy": "निरोगी",
        "continue_monitoring": "निरीक्षण सुरू ठेवा",

        "issues_detected": "आढळलेल्या समस्या",
        "review_recommendations": "शिफारशी पहा",

        "recent_scans": "अलीकडील तपासण्या",

        "recent_scans_empty": (
            "तुमच्या अलीकडील तपासण्या येथे दिसतील."
        ),

        "confidence_short": "विश्वास",

        "weather_risk_insight": "हवामान जोखीम माहिती",

        "weather_risk_high": (
            "दमट किंवा ओलसर परिस्थितीमुळे काही बुरशीजन्य रोगांचा "
            "धोका वाढू शकतो. हवेचा प्रवाह सुधारावा आणि पानांवर "
            "अनावश्यक ओलावा राहू देऊ नये."
        ),

        "weather_risk_low": (
            "सध्याची परिस्थिती पाने कोरडी होण्यासाठी अनुकूल आहे. "
            "पिकाची नियमित तपासणी सुरू ठेवा."
        ),

        "risk_disclaimer": (
            "ही केवळ पिकाच्या जोखमीची माहिती आहे, अंतिम निदान नाही."
        ),

        "how_cropguard_works": "CropGuard कसे कार्य करते",

        "step_find_farm": "तुमचे शेत शोधा",
        "step_find_farm_body": (
            "स्थान आणि हवामानाची माहिती वापरा."
        ),

        "step_capture_leaf": "पानाचा फोटो घ्या",
        "step_capture_leaf_body": (
            "कॅमेऱ्याचा वापर करा किंवा फोटो निवडा."
        ),

        "step_next_step": "पुढील कृती करा",
        "step_next_step_body": (
            "विश्वास पातळी, धोका आणि आयपीएम मार्गदर्शन पहा."
        ),

        "footer_disclaimer": (
            "CropGuard निर्णय सहाय्य देते. "
            "अनिश्चित प्रकरणांची खात्री पात्र कृषी तज्ज्ञ "
            "किंवा प्रयोगशाळेकडून करून घ्या."
        ),
    },
}


# =========================================================
# DISEASE NAMES
# =========================================================

DISEASE_NAMES = {

    # -----------------------------------------------------
    # English
    # -----------------------------------------------------
    "en": {
        "Early Blight": "Early Blight",
        "Late Blight": "Late Blight",
        "Healthy": "Healthy",
        "Pink Bollworm": "Pink Bollworm",
        "Aphids": "Aphids",
        "Whitefly": "Whitefly",
        "Fall Armyworm": "Fall Armyworm",
        "Leaf Blight": "Leaf Blight",
        "Blast": "Blast",
        "Brown Spot": "Brown Spot",
        "Rust": "Rust",
        "Powdery Mildew": "Powdery Mildew",
        "Mosaic Virus": "Mosaic Virus",
    },

    # -----------------------------------------------------
    # Hindi
    # -----------------------------------------------------
    "hi": {
        "Early Blight": "अर्ली ब्लाइट",
        "Late Blight": "लेट ब्लाइट",
        "Healthy": "स्वस्थ",
        "Pink Bollworm": "गुलाबी इल्ली",
        "Aphids": "माहू",
        "Whitefly": "सफेद मक्खी",
        "Fall Armyworm": "फॉल आर्मीवर्म",
        "Leaf Blight": "पत्ती झुलसा",
        "Blast": "ब्लास्ट",
        "Brown Spot": "भूरा धब्बा",
        "Rust": "रतुआ",
        "Powdery Mildew": "चूर्णिल आसिता",
        "Mosaic Virus": "मोज़ेक विषाणु",
    },

    # -----------------------------------------------------
    # Marathi
    # -----------------------------------------------------
    "mr": {
        "Early Blight": "अर्ली ब्लाइट",
        "Late Blight": "लेट ब्लाइट",
        "Healthy": "निरोगी",
        "Pink Bollworm": "गुलाबी बोंड अळी",
        "Aphids": "मावा",
        "Whitefly": "पांढरी माशी",
        "Fall Armyworm": "फॉल आर्मीवर्म",
        "Leaf Blight": "पान करपा",
        "Blast": "ब्लास्ट",
        "Brown Spot": "तपकिरी ठिपके",
        "Rust": "तांबेरा",
        "Powdery Mildew": "भुरी",
        "Mosaic Virus": "मोझॅक विषाणू",
    },
}


# =========================================================
# TRANSLATION FUNCTION
# =========================================================

def t(lang: str, key: str) -> str:
    """
    Return the translated UI string.

    Falls back to English if:
      - language code is unsupported
      - requested translation does not exist

    If the key does not exist in English either,
    the key itself is returned.
    """

    # Validate language
    lang = lang if lang in STRINGS else "en"

    # Get requested language
    translated = STRINGS.get(lang, {})

    # Return requested translation
    if key in translated:
        return translated[key]

    # Fallback to English
    english = STRINGS.get("en", {})

    if key in english:
        return english[key]

    # Final fallback
    return key


# =========================================================
# DISEASE TRANSLATION FUNCTION
# =========================================================

def translate_disease(lang: str, name: str) -> str:
    """
    Translate an AI disease/pest prediction.

    Falls back to the original disease name when no
    translation exists.
    """

    lang = lang if lang in DISEASE_NAMES else "en"

    return DISEASE_NAMES[lang].get(name, name)