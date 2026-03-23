let recognition;
let listening = false;

function setStatus(t){
    document.getElementById("status").innerText = t;
}

function setListening(on){
    let mic = document.querySelector(".mic");
    let core = document.querySelector(".core");

    if(on){
        mic.classList.add("active");
        core.classList.add("listening");
    } else {
        mic.classList.remove("active");
        core.classList.remove("listening");
    }
}

function speak(text){
    let s = new SpeechSynthesisUtterance(text);
    setStatus("🔊 Speaking...");
    speechSynthesis.speak(s);
    s.onend = ()=> startWakeWord(); // go back to wake mode
}

async function send(q){
    setStatus("Processing...");

    let res = await fetch("/ask",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({q})
    });

    let data = await res.json();

    document.getElementById("chat").innerHTML += `<div class='msg user'>${q}</div>`;
    document.getElementById("chat").innerHTML += `<div class='msg bot'>${data.answer}</div>`;

    speak(data.answer);
}

function startWakeWord(){
    recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = "en-US";
    recognition.continuous = true;

    setStatus("💤 Waiting for 'Jarvis'...");
    setListening(false);

    recognition.onresult = (e)=>{
        let text = e.results[e.results.length - 1][0].transcript.toLowerCase();

        if(text.includes("jarvis")){
            recognition.stop();
            startListening();
        }
    };

    recognition.start();
}

function startListening(){
    recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = "en-US";

    setListening(true);
    setStatus("🎤 Listening...");

    recognition.onresult = (e)=>{
        let text = e.results[0][0].transcript;
        send(text);
    };

    recognition.onend = ()=>{
        setListening(false);
    };

    recognition.start();
}

// START AUTOMATICALLY
window.onload = () => {
    startWakeWord();
};
