const chatInput = document.querySelector(".chat-input textarea");
const sendChatBtn = document.querySelector(".chat-input span");
const chatbox = document.querySelector(".chatbox");
const chatbotToggler = document.querySelector(".chatbot-toggler");
const chatbotCloseBtn = document.querySelector(".close-btn");

let userMessage;
const API_KEY = "";

const createChatLi = (message, className) => {
    // Create a new li element
    const chatLi = document.createElement("li");
    chatLi.classList.add("chat", className);
    
    let chatContent = className === "outgoing" ? `<p></p>` : `<span class="material-symbols-outlined">smart_toy</span><p></p>`;
    chatLi.innerHTML = chatContent; 
    chatLi.querySelector("p").textContent = message;
    return chatLi;
}

const generateResponse = (incomingChatLi) => {
    const API_URL = " https://api.openai.com/v1/chat/completions";
    const messageElement = incomingChatLi.querySelector("p");


    const requestOptions  = {
        method: "POST",
        headers:{
                'Content-Type': "application/json",
                "Authorization":`Bearer ${API_KEY}`
        },
        body: JSON.stringify({
            model: "gpt-3.5-turbo",
            messages: [{role: "user", content: userMessage}]
        })
    }
    
    // Send POST req to API, gets response
    fetch(API_URL, requestOptions).then(res => res.json()).then(data => {
        messageElement.textContent =data.choices[0].message.content;
    }).catch((error)=>{
        messageElement.textContent = "Something went wrong. Please try again...";
    }).finally(() => chatbox.scrollTo(0, chatbox.scrollHeight));

}


const handleChat = () => {
    userMessage = chatInput.value.trim();
    if(!userMessage) return;
    chatInput.value = "";



    // Append user message to chatbox
    chatbox.appendChild(createChatLi(userMessage, "outgoing")); 
    chatbox.scrollTo(0,chatbox.scrollHeight);



    //chatInput.value = ""; // Clear the input field after sending the message
    setTimeout(() => {
        const incomingChatLi = createChatLi("Divining...", "incoming");
        chatbox.appendChild(incomingChatLi); 
        chatbox.scrollTo(0, chatbox.scrollHeight);  
        generateResponse(incomingChatLi);
    }, 600);
}

sendChatBtn.addEventListener("click", handleChat);
chatbotToggler.addEventListener("click", () => document.body.classList.toggle("show-chatbot"));
