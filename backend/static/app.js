async function createPoll() {
    const question = document.getElementById("question").value;
    const option1 = document.getElementById("option1").value;
    const option2 = document.getElementById("option2").value;
    const option3 = document.getElementById("option3").value;

    const options = [option1,option2,option3].filter(option => option.trim() !== "");

    const response = await fetch("/polls", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ 
            question:question, 
            options:options 
        })
    });

        const data = await response.json();
        console.log(data);
        loadPolls();
}


async function loadPolls(){
    const response = await fetch("/polls");
    const polls = await response.json();

    const container = document.getElementById("pollsContainer");
    container.innerHTML = "";

    for (const poll of polls){
        const pollDiv = document.createElement("div");
         let optionsHtml = "";

         for(const option of poll.options){
            optionsHtml+= `
            <li>
                ${option.text} - ${option.votes} votes
                <button onclick="vote(${poll.id}, ${option.id})">Vote</button>
            </li>
            `;  
         }


        pollDiv.innerHTML = `
            <h3>${poll.question}</h3>
            <ul>
                ${optionsHtml}
            </ul>
            <button onclick="deletePoll(${poll.id})">Delete Poll</button>
            `;

        container.appendChild(pollDiv); 
    
    }
}



async function vote(pollId, optionId){
    const response = await fetch(`/polls/${pollId}/vote`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ option_id: optionId })
    });

    const data = await response.json();
    console.log(data);
    loadPolls();
}

async function deletePoll(pollId){
    const response = await fetch(`/polls/${pollId}`, {
        method: "DELETE"
    });
    loadPolls();
}
