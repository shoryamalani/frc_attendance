
// everytime a name is typed into name_search_box the following function is called after 1 second and the value changed
// Get the search box element
const searchBox = document.getElementById('name_search_box');
const teamNumber = document.getElementById('team_number').textContent;

    const namesList = document.getElementById('names_list');
console.log(teamNumber)
var membersArray = []
let selectedMemberIds = new Set(); // Set to keep track of selected member IDs

var xhr = new XMLHttpRequest();

xhr.open('POST', '/api/teamMembers', true);
xhr.setRequestHeader('Content-Type', 'application/json');
var data = {
    teamNumber: teamNumber
}
xhr.send(JSON.stringify(data));

xhr.onload = function() {
    if(xhr.status === 200) {
        data = JSON.parse(xhr.responseText);
        membersArray = data.teamMembers;
        // console.log(teamMembers)
    } else {
        alert('Error finding team.');
    }
};


function handleSearch() {
    const searchText = searchBox.value.toLowerCase();
    namesList.innerHTML = ''; // Clear existing names
    if (selectedMemberIds.size === 0){
        document.getElementById("signInButton").setAttribute('disabled', true);
        document.getElementById("signInButton").classList.add('bg-gray-200');
        document.getElementById("signInButton").classList.remove('bg-blue-600');
        // set sign out button color to gray


        document.getElementById("signOutButton").setAttribute('disabled', true);
        document.getElementById("signOutButton").classList.add('bg-gray-200');
        document.getElementById("signOutButton").classList.remove('bg-blue-600');
    }
    else{
        document.getElementById("signInButton").removeAttribute('disabled');
        document.getElementById("signInButton").classList.add('bg-blue-600');
        document.getElementById("signInButton").classList.remove('bg-gray-200');
        // remove gray from sign out button


        document.getElementById("signOutButton").classList.add('bg-blue-600');
        document.getElementById("signOutButton").removeAttribute('disabled');
        document.getElementById("signOutButton").classList.remove('bg-gray-200');
    }
 // Add selected members to the list
 selectedMemberIds.forEach(id => {
    const member = membersArray.find(m => m.id === id);
    if (member) {
        addMemberButton(member, true);
    }
});

sign = function(isSignIn) {
    // Get the selected members
    const selectedMembers = [];
    selectedMemberIds.forEach(id => {
        // only get the ids
        selectedMembers.push(id);
    });

    // Send the request to the server
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/sign', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({
        teamNumber: teamNumber,
        members: selectedMembers,
        isSignIn: isSignIn
    }));
    xhr.onload = function() {
        if (xhr.status === 200) {
            // Refresh the page
            alert('Success!');
            location.reload();
        } else {
            alert('Error signing in/out.');
        }
    }
}

// Add members matching the search text
if (searchText.length > 0) {
    membersArray.forEach(member => {
        if (member.name.toLowerCase().includes(searchText) && !selectedMemberIds.has(member.id)) {
            addMemberButton(member, false);
        }
    });
}
    
}
function addMemberButton(member, isSelected) {
    const memberButton = document.createElement('button');
    memberButton.textContent = `${member.name} (${member.year}, ${member.subteam})`;
    memberButton.classList.add('p-2', 'hover:bg-gray-100', 'w-full', 'text-left', 'mb-2');
    if (isSelected) {
        memberButton.classList.add('bg-gray-200'); // Different background for selected members
    }
    memberButton.onclick = function() {
        if (!selectedMemberIds.has(member.id)) {
            selectedMemberIds.add(member.id); // Add ID to selected member IDs
            handleSearch(); // Refresh display
        }
    };
    namesList.appendChild(memberButton);
}

// Timeout variable to keep track of the timer
let timeout = null;

// Event listener for keyup event
searchBox.addEventListener('keyup', function() {
    // Clear the previous timeout if it exists
    clearTimeout(timeout);

    // Set a new timeout
    timeout = setTimeout(handleSearch, 200);
});
