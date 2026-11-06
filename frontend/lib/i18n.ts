export type Lang = "te-IN" | "hi-IN" | "en-IN";
export const LANGS: { code: Lang; native: string; english: string }[] = [
  { code: "te-IN", native: "తెలుగు", english: "Telugu" },
  { code: "hi-IN", native: "हिन्दी", english: "Hindi" },
  { code: "en-IN", native: "English", english: "English" },
];

const T = {
  "te-IN": {
    tap: "మాట్లాడటానికి నొక్కండి", listening: "వింటున్నాను… ఆపడానికి నొక్కండి", processing: "మీ ప్రశ్నను అర్థం చేసుకుంటున్నాను…",
    you: "మీరు అడిగినది", answer: "RythuVoice సమాధానం", replay: "మళ్ళీ వినండి", history: "గత సంభాషణలు", empty: "ఇంకా సంభాషణలు లేవు",
    settings: "సెట్టింగ్స్", autoplay: "సమాధానం ఆటోమేటిక్‌గా వినిపించు", clear: "చరిత్ర తొలగించు", photo: "పంట ఫోటో విశ్లేషించండి", sources: "ఆధారాలు",
    followup: "తదుపరి ప్రశ్న అడగండి", typeQuestion: "మీ ప్రశ్నను టైప్ చేయండి", placeholder: "ఉదా: నా వరి ఆకులు పసుపు రంగులోకి మారుతున్నాయి…",
    send: "పంపండి", orSpeak: "లేదా మాట్లాడండి", weather: "3 రోజుల వాతావరణం", useLocation: "నా ప్రాంత వాతావరణం", cityPlaceholder: "గ్రామం లేదా పట్టణం పేరు", search: "వాతావరణం చూడండి",
    locationDenied: "లొకేషన్ అనుమతి లేదు. మీ గ్రామం లేదా పట్టణం పేరును నమోదు చేయండి.", current: "ప్రస్తుతం", humidity: "తేమ", wind: "గాలి వేగం", rain: "వర్షం", minMax: "కనిష్టం–గరిష్టం",
    photoNote: "పంట పేరు / పెరుగుదల దశ (ఐచ్ఛికం)", photoNotePlaceholder: "ఉదా: వరి, పిలకలు వచ్చే దశ", photoAnalyzing: "ఫోటోను విశ్లేషిస్తున్నాను…", photoError: "ఫోటో విశ్లేషణ విఫలమైంది.",
    micDenied: "మైక్రోఫోన్ అనుమతి లేదు. బ్రౌజర్ సెట్టింగ్స్‌లో అనుమతించండి.", answerSpeechError: "సమాధానం సిద్ధంగా ఉంది, కానీ ఆడియో రూపొందించలేకపోయాం: ",
    crops: "పంటలు", cropsDesc: "వరి, పత్తి, మిరప, మొక్కజొన్న మరియు ఇతర పంటలపై ప్రశ్నలు.", pests: "చీడపీడలు మరియు వ్యాధులు", pestsDesc: "లక్షణాలను వివరించండి లేదా ఫోటో పంపండి. అవసరమైతే నిపుణుడిని సంప్రదించండి.",
    soil: "నేల ఆరోగ్యం", soilDesc: "నేల, పోషకాలు మరియు ఎరువులపై సురక్షితమైన సూచనలు.", irrigation: "నీటిపారుదల", irrigationDesc: "పంట దశకు అనుగుణంగా నీటి నిర్వహణ.", harvest: "కోత", harvestDesc: "కోత మరియు నిల్వ విధానాలు.", schemes: "ప్రభుత్వ పథకాలు", schemesDesc: "పథకాల వివరాలను వ్యవసాయ అధికారితో నిర్ధారించుకోండి."
  },
  "hi-IN": {
    tap: "बोलने के लिए दबाएँ", listening: "सुन रहा हूँ… रोकने के लिए दबाएँ", processing: "आपका सवाल समझ रहा हूँ…",
    you: "आपने पूछा", answer: "RythuVoice का जवाब", replay: "फिर सुनें", history: "पिछली बातचीत", empty: "अभी कोई बातचीत नहीं",
    settings: "सेटिंग्स", autoplay: "जवाब अपने आप सुनाएँ", clear: "इतिहास हटाएँ", photo: "फसल की फोटो जाँचें", sources: "स्रोत",
    followup: "अगला सवाल पूछें", typeQuestion: "अपना सवाल लिखें", placeholder: "उदाहरण: धान की पत्तियाँ पीली हो रही हैं…",
    send: "भेजें", orSpeak: "या बोलकर पूछें", weather: "3 दिन का मौसम", useLocation: "मेरे स्थान का मौसम", cityPlaceholder: "गाँव या शहर का नाम", search: "मौसम देखें",
    locationDenied: "स्थान की अनुमति नहीं मिली। अपने गाँव या शहर का नाम लिखें।", current: "अभी", humidity: "नमी", wind: "हवा की गति", rain: "बारिश", minMax: "न्यूनतम–अधिकतम",
    photoNote: "फसल / बढ़ने की अवस्था (वैकल्पिक)", photoNotePlaceholder: "उदाहरण: धान, कल्ले निकलने की अवस्था", photoAnalyzing: "फोटो की जाँच हो रही है…", photoError: "फोटो का विश्लेषण नहीं हो सका।",
    micDenied: "माइक्रोफोन की अनुमति नहीं है। ब्राउज़र सेटिंग में अनुमति दें।", answerSpeechError: "जवाब तैयार है, लेकिन ऑडियो नहीं बन सका: ",
    crops: "फसलें", cropsDesc: "धान, कपास, मिर्च, मक्का और अन्य फसलों के सवाल।", pests: "कीट और रोग", pestsDesc: "लक्षण बताएँ या फोटो भेजें। ज़रूरत पर विशेषज्ञ से मिलें।",
    soil: "मिट्टी का स्वास्थ्य", soilDesc: "मिट्टी, पोषक तत्व और खाद के बारे में सुरक्षित सलाह।", irrigation: "सिंचाई", irrigationDesc: "फसल की अवस्था के अनुसार पानी का प्रबंधन।", harvest: "कटाई", harvestDesc: "कटाई और भंडारण के तरीके।", schemes: "सरकारी योजनाएँ", schemesDesc: "योजनाओं की जानकारी कृषि अधिकारी से जाँचें।"
  },
  "en-IN": {
    tap: "Tap to speak", listening: "Listening… tap to stop", processing: "Understanding your question…",
    you: "You asked", answer: "RythuVoice answer", replay: "Replay", history: "Past conversations", empty: "No conversations yet",
    settings: "Settings", autoplay: "Auto-play answers", clear: "Clear history", photo: "Analyse a crop photo", sources: "Sources",
    followup: "Ask a follow-up", typeQuestion: "Type your question", placeholder: "Example: My paddy leaves are turning yellow…",
    send: "Send", orSpeak: "Or ask by speaking", weather: "3-day weather", useLocation: "Use my location", cityPlaceholder: "Village or town name", search: "Get weather",
    locationDenied: "Location permission was denied. Enter your village or town instead.", current: "Current", humidity: "Humidity", wind: "Wind", rain: "Rain", minMax: "Low–high",
    photoNote: "Crop name / growth stage (optional)", photoNotePlaceholder: "Example: Paddy, tillering stage", photoAnalyzing: "Analysing your photo…", photoError: "Could not analyse the photo.",
    micDenied: "Microphone permission denied. Allow it in your browser settings.", answerSpeechError: "Your answer is ready, but audio could not be generated: ",
    crops: "Crops", cropsDesc: "Questions about paddy, cotton, chilli, maize and other crops.", pests: "Pests & diseases", pestsDesc: "Describe symptoms or send a photo. Consult an expert when needed.",
    soil: "Soil health", soilDesc: "Safe guidance about soil, nutrients and fertilizers.", irrigation: "Irrigation", irrigationDesc: "Water management for each crop stage.", harvest: "Harvesting", harvestDesc: "Harvesting and storage practices.", schemes: "Government schemes", schemesDesc: "Verify scheme details with your agriculture officer."
  }
} as const;
export const t = (l: Lang) => T[l];
