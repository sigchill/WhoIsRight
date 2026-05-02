async function createPoll() {
    const question = document.getElementById("question").value;
    const option1 = document.getElementById("option1").value;
    const option2 = document.getElementById("option2").value;
    const option3 = document.getElementById("option3").value;

    const options = [option1, option2, option3].filter(option => option.trim() !== "");

    const response = await fetch("/polls", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            question: question,
            options: options
        })
    });

    const data = await response.json();

    if (!response.ok) {
        alert("Error: " + data.detail);
        return;
    }

    console.log(data);

    document.getElementById("question").value = "";
    document.getElementById("option1").value = "";
    document.getElementById("option2").value = "";
    document.getElementById("option3").value = "";

    await loadPolls();
}

//submit a vote for a poll
async function submitVote(pollId) {
    const playerName = document.getElementById(`playerName=${pollId}`).value;
    const voteOptionId = document.getElementById(`voteOption=${pollId}`).value;
    const predictionOptionId = document.getElementById(`predictionOption=${pollId}`).value;

    const response = await fetch(`/polls/${pollId}/submit`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            player_name: playerName,
            voted_option_id: parseInt(voteOptionId),
            predicted_winner_option_id: parseInt(predictionOptionId)
        })
    });

    const data = await response.json();

    if (!response.ok) {
        alert("Error: " + data.detail);
        return;
    }

    console.log(data);
    alert("Submission saved");

    await loadPolls();
    await loadResults(pollId);
}



//load results of a poll
async function loadResults(pollId) {
    const response = await fetch(`/polls/${pollId}/results`);
    const data = await response.json();

    const resultDiv = document.getElementById(`results-${pollId}`);

    if (!resultDiv) {
        console.error(`Missing results div for poll ${pollId}`);
        return;
    }

    if (!response.ok) {
        resultDiv.innerHTML = "Error loading results";
        return;
    }

    let optionsHtml = "";

    for (const option of data.options) {
        optionsHtml += `
            <li>
                ${option.text}: ${option.votes} votes
            </li>
        `;
    }

    resultDiv.innerHTML = `
        <h4>Current Results:</h4>
        <p>Total votes: ${data.total_votes}</p>
        <ul>
            ${optionsHtml}
        </ul>
    `;
}


async function loadPolls() {
    const response = await fetch("/polls");
    const polls = await response.json();

    const container = document.getElementById("pollsContainer");
    container.innerHTML = "";

    for (const poll of polls) {
        const pollDiv = document.createElement("div");
        pollDiv.className = "poll";

        let voteOptionsHtml = "";
        let predictionOptionsHtml = "";

        for (const option of poll.options) {
            voteOptionsHtml += `
                <option value="${option.id}">${option.text}</option>
            `;

            predictionOptionsHtml += `
                <option value="${option.id}">${option.text}</option>
            `;
        }

        pollDiv.innerHTML = `
            <h3>${poll.question}</h3>

            <p>
                Status:
                <span class="${poll.is_closed ? "closed" : "open"}">
                    ${poll.is_closed ? "Closed" : "Open"}
                </span>
            </p>

            <input id="playerName=${poll.id}" placeholder="Your Name" />

            <label>Your vote</label>
            <select id="voteOption=${poll.id}">
                ${voteOptionsHtml}
            </select>

            <label>Your prediction for majority vote</label>
            <select id="predictionOption=${poll.id}">
                ${predictionOptionsHtml}
            </select>

            <button onclick="submitVote(${poll.id})">Submit Vote</button>
            <button onclick="deletePoll(${poll.id})">Delete Poll</button>

            <div id="results-${poll.id}"></div>
        `;

        container.appendChild(pollDiv);

    }
}


async function deletePoll(pollId) {
    const response = await fetch(`/polls/${pollId}`, {
        method: "DELETE"
    });

    const data = await response.json();

    if (!response.ok) {
        alert("Error: " + data.detail);
        return;
    }

    await loadPolls();
}


// Automatically load polls when page opens
loadPolls();