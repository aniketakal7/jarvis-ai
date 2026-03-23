function typeEffect(text, element) {
    let i = 0;
    function typing() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            setTimeout(typing, 15);
        }
    }
    typing();
}

function add(msg, cls){
    let d=document.createElement("div");
    d.className=cls;
    document.getElementById("chat").appendChild(d);

    if(cls==="bot"){
        typeEffect(msg,d);
    } else {
        d.innerText=msg;
    }
}

function showThinking(){
    let d=document.createElement("div");
    d.className="bot";
    d.id="thinking";
    d.innerText="Jarvis thinking...";
    document.getElementById("chat").appendChild(d);
}

function removeThinking(){
    let t=document.getElementById("thinking");
    if(t) t.remove();
}

function send(){
    let q=document.getElementById("q").value;
    add(q,"user");

    showThinking();

    fetch("/ask",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({q:q})
    })
    .then(r=>r.json())
    .then(d=>{
        removeThinking();
        add(d.answer,"bot");
    });

    document.getElementById("q").value="";
}

// 🎙️ Auto listening
function startListening(){
    let r=new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    r.continuous=true;

    r.onresult=function(e){
        let text=e.results[e.results.length-1][0].transcript.toLowerCase();

        if(text.includes("jarvis")){
            document.getElementById("q").value=text.replace("jarvis","").trim();
            send();
        }
    };

    r.start();
}

startListening();
