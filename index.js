const API_URL = 'http://127.0.0.1:5000/api';

// Tab Navigation
function showTab(tabName) {
    const tabs = document.querySelectorAll('.tab-content');
    const btns = document.querySelectorAll('.tab-btn');
    
    tabs.forEach(tab => tab.classList.remove('active'));
    btns.forEach(btn => btn.classList.remove('active'));
    
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
    
    // Load data when tab is opened
    if (tabName === 'members') loadMembers();
    if (tabName === 'trainers') loadTrainers();
    if (tabName === 'memberships') loadMemberships();
    if (tabName === 'workouts') loadWorkouts();
    if (tabName === 'diets') loadDiets();
    if (tabName === 'vitals') loadVitals();
}

// Show Alert Messages
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    const container = document.querySelector('.tab-content.active');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => alertDiv.remove(), 3000);
}

// ==================== MEMBERS ====================
document.getElementById('memberForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const data = {
        name: document.getElementById('memberName').value,
        dob: document.getElementById('memberDOB').value,
        join_date: document.getElementById('memberJoinDate').value,
        email: document.getElementById('memberEmail').value
    };
    
    try {
        const response = await fetch(`${API_URL}/members`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showAlert('Member added successfully!', 'success');
            document.getElementById('memberForm').reset();
            loadMembers();
        }
    } catch (error) {
        showAlert('Error adding member', 'error');
    }
});

async function loadMembers() {
    try {
        const response = await fetch(`${API_URL}/members`);
        const members = await response.json();
        
        const tbody = document.querySelector('#membersTable tbody');
        tbody.innerHTML = '';
        
        members.forEach(member => {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${member.member_id}</td>
                <td>${member.name}</td>
                <td>${member.dob || '-'}</td>
                <td>${member.join_date || '-'}</td>
                <td>${member.email || '-'}</td>
                <td>
                    <button class="btn btn-delete" onclick="deleteMember(${member.member_id})">Delete</button>
                </td>
            `;
        });
        
        // Update dropdowns
        updateMemberDropdowns(members);
    } catch (error) {
        console.error('Error loading members:', error);
    }
}

async function deleteMember(id) {
    if (!confirm('Are you sure you want to delete this member? This will also delete all their memberships and vitals records.')) return;
    
    try {
        const response = await fetch(`${API_URL}/members/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showAlert('Member and all related records deleted successfully!', 'success');
            loadMembers();
            loadMemberships(); // Refresh memberships as they might reference deleted member
            loadVitals(); // Refresh vitals as they might reference deleted member
        }
    } catch (error) {
        showAlert('Error deleting member', 'error');
    }
}

function updateMemberDropdowns(members) {
    const dropdowns = ['membershipMember', 'vitalsMember'];
    
    dropdowns.forEach(dropdownId => {
        const select = document.getElementById(dropdownId);
        select.innerHTML = '<option value="">Select Member</option>';
        
        members.forEach(member => {
            const option = document.createElement('option');
            option.value = member.member_id;
            option.textContent = member.name;
            select.appendChild(option);
        });
    });
}

// ==================== TRAINERS ====================
document.getElementById('trainerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const data = {
        name: document.getElementById('trainerName').value,
        specialisation: document.getElementById('trainerSpec').value
    };
    
    try {
        const response = await fetch(`${API_URL}/trainers`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showAlert('Trainer added successfully!', 'success');
            document.getElementById('trainerForm').reset();
            loadTrainers();
        }
    } catch (error) {
        showAlert('Error adding trainer', 'error');
    }
});

async function loadTrainers() {
    try {
        const response = await fetch(`${API_URL}/trainers`);
        const trainers = await response.json();
        
        const tbody = document.querySelector('#trainersTable tbody');
        tbody.innerHTML = '';
        
        trainers.forEach(trainer => {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${trainer.trainer_id}</td>
                <td>${trainer.name}</td>
                <td>${trainer.specialisation || '-'}</td>
                <td>
                    <button class="btn btn-delete" onclick="deleteTrainer(${trainer.trainer_id})">Delete</button>
                </td>
            `;
        });
        
        // Update dropdowns
        updateTrainerDropdowns(trainers);
    } catch (error) {
        console.error('Error loading trainers:', error);
    }
}

async function deleteTrainer(id) {
    if (!confirm('Are you sure you want to delete this trainer? This will remove trainer assignments from related plans and memberships.')) return;
    
    try {
        const response = await fetch(`${API_URL}/trainers/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showAlert('Trainer deleted successfully and references updated!', 'success');
            loadTrainers();
            loadMemberships(); // Refresh memberships as they might reference deleted trainer
            loadWorkouts(); // Refresh workouts as they might reference deleted trainer
            loadDiets(); // Refresh diets as they might reference deleted trainer
        }
    } catch (error) {
        showAlert('Error deleting trainer', 'error');
    }
}

function updateTrainerDropdowns(trainers) {
    const dropdowns = ['workoutTrainer', 'dietTrainer'];
    
    dropdowns.forEach(dropdownId => {
        const select = document.getElementById(dropdownId);
        select.innerHTML = '<option value="">Select Trainer (Optional)</option>';
        
        trainers.forEach(trainer => {
            const option = document.createElement('option');
            option.value = trainer.trainer_id;
            option.textContent = trainer.name;
            select.appendChild(option);
        });
    });
}

// ==================== MEMBERSHIPS ====================
document.getElementById('membershipForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const data = {
        membership_type: document.getElementById('membershipType').value,
        start_date: document.getElementById('membershipStart').value,
        end_date: document.getElementById('membershipEnd').value,
        payment_type: document.getElementById('membershipPayment').value,
        payment_amount: parseFloat(document.getElementById('membershipAmount').value),
        status: document.getElementById('membershipStatus').value,
        member_id: parseInt(document.getElementById('membershipMember').value)
    };
    
    try {
        const response = await fetch(`${API_URL}/memberships`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showAlert('Membership added successfully!', 'success');
            document.getElementById('membershipForm').reset();
            loadMemberships();
        }
    } catch (error) {
        showAlert('Error adding membership', 'error');
    }
});

async function loadMemberships() {
    try {
        const response = await fetch(`${API_URL}/memberships`);
        const memberships = await response.json();
        
        const tbody = document.querySelector('#membershipsTable tbody');
        tbody.innerHTML = '';
        
        memberships.forEach(membership => {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${membership.membership_id}</td>
                <td>${membership.member_name || 'N/A'}</td>
                <td>${membership.membership_type}</td>
                <td>${membership.start_date}</td>
                <td>${membership.end_date}</td>
                <td>₹${membership.payment_amount}</td>
                <td><span class="status-${membership.status.toLowerCase()}">${membership.status}</span></td>
                <td>
                    <button class="btn btn-delete" onclick="deleteMembership(${membership.membership_id})">Delete</button>
                </td>
            `;
        });
    } catch (error) {
        console.error('Error loading memberships:', error);
    }
}

async function deleteMembership(id) {
    if (!confirm('Are you sure you want to delete this membership?')) return;
    
    try {
        const response = await fetch(`${API_URL}/memberships/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showAlert('Membership deleted successfully!', 'success');
            loadMemberships();
        }
    } catch (error) {
        showAlert('Error deleting membership', 'error');
    }
}

// ==================== WORKOUTS ====================
document.getElementById('workoutForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const trainerId = document.getElementById('workoutTrainer').value;
    
    const data = {
        plan_name: document.getElementById('workoutName').value,
        description: document.getElementById('workoutDesc').value,
        intensity_level: document.getElementById('workoutIntensity').value,
        trainer_id: trainerId ? parseInt(trainerId) : null
    };
    
    try {
        const response = await fetch(`${API_URL}/workouts`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showAlert('Workout plan added successfully!', 'success');
            document.getElementById('workoutForm').reset();
            loadWorkouts();
        }
    } catch (error) {
        showAlert('Error adding workout plan', 'error');
    }
});

async function loadWorkouts() {
    try {
        const response = await fetch(`${API_URL}/workouts`);
        const workouts = await response.json();
        
        const tbody = document.querySelector('#workoutsTable tbody');
        tbody.innerHTML = '';
        
        workouts.forEach(workout => {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${workout.plan_id}</td>
                <td>${workout.plan_name}</td>
                <td>${workout.description || '-'}</td>
                <td>${workout.intensity_level}</td>
                <td>${workout.trainer_name || 'N/A'}</td>
                <td>
                    <button class="btn btn-delete" onclick="deleteWorkout(${workout.plan_id})">Delete</button>
                </td>
            `;
        });
    } catch (error) {
        console.error('Error loading workouts:', error);
    }
}

async function deleteWorkout(id) {
    if (!confirm('Are you sure you want to delete this workout plan? This will remove the plan from any associated memberships.')) return;
    
    try {
        const response = await fetch(`${API_URL}/workouts/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showAlert('Workout plan deleted successfully!', 'success');
            loadWorkouts();
            loadMemberships(); // Refresh memberships as they might reference deleted workout plan
        }
    } catch (error) {
        showAlert('Error deleting workout plan', 'error');
    }
}

// ==================== DIET PLANS ====================
document.getElementById('dietForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const trainerId = document.getElementById('dietTrainer').value;
    
    const data = {
        dietplan_name: document.getElementById('dietName').value,
        diet_description: document.getElementById('dietDesc').value,
        target_calories: parseInt(document.getElementById('dietCalories').value),
        trainer_id: trainerId ? parseInt(trainerId) : null
    };
    
    try {
        const response = await fetch(`${API_URL}/diets`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showAlert('Diet plan added successfully!', 'success');
            document.getElementById('dietForm').reset();
            loadDiets();
        }
    } catch (error) {
        showAlert('Error adding diet plan', 'error');
    }
});

async function loadDiets() {
    try {
        const response = await fetch(`${API_URL}/diets`);
        const diets = await response.json();
        
        const tbody = document.querySelector('#dietsTable tbody');
        tbody.innerHTML = '';
        
        diets.forEach(diet => {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${diet.dietplan_id}</td>
                <td>${diet.dietplan_name}</td>
                <td>${diet.diet_description || '-'}</td>
                <td>${diet.target_calories}</td>
                <td>${diet.trainer_name || 'N/A'}</td>
                <td>
                    <button class="btn btn-delete" onclick="deleteDiet(${diet.dietplan_id})">Delete</button>
                </td>
            `;
        });
    } catch (error) {
        console.error('Error loading diets:', error);
    }
}

async function deleteDiet(id) {
    if (!confirm('Are you sure you want to delete this diet plan? This will remove the plan from any associated memberships.')) return;
    
    try {
        const response = await fetch(`${API_URL}/diets/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showAlert('Diet plan deleted successfully!', 'success');
            loadDiets();
            loadMemberships(); // Refresh memberships as they might reference deleted diet plan
        }
    } catch (error) {
        showAlert('Error deleting diet plan', 'error');
    }
}

// ==================== VITALS ====================
document.getElementById('vitalsForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const data = {
        weight: parseFloat(document.getElementById('vitalsWeight').value),
        height: parseFloat(document.getElementById('vitalsHeight').value),
        record_date: document.getElementById('vitalsDate').value,
        memb_id: parseInt(document.getElementById('vitalsMember').value)
    };
    
    try {
        const response = await fetch(`${API_URL}/vitals`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showAlert('Vitals recorded successfully!', 'success');
            document.getElementById('vitalsForm').reset();
            loadVitals();
        }
    } catch (error) {
        showAlert('Error recording vitals', 'error');
    }
});

async function loadVitals() {
    try {
        const response = await fetch(`${API_URL}/vitals`);
        const vitals = await response.json();
        
        const tbody = document.querySelector('#vitalsTable tbody');
        tbody.innerHTML = '';
        
        vitals.forEach(vital => {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${vital.vitals_id}</td>
                <td>${vital.member_name || 'N/A'}</td>
                <td>${vital.weight} kg</td>
                <td>${vital.height} cm</td>
                <td>${vital.record_date}</td>
                <td>
                    <button class="btn btn-delete" onclick="deleteVitals(${vital.vitals_id})">Delete</button>
                </td>
            `;
        });
    } catch (error) {
        console.error('Error loading vitals:', error);
    }
}

async function deleteVitals(id) {
    if (!confirm('Are you sure you want to delete this vitals record?')) return;
    
    try {
        const response = await fetch(`${API_URL}/vitals/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showAlert('Vitals record deleted successfully!', 'success');
            loadVitals();
        }
    } catch (error) {
        showAlert('Error deleting vitals record', 'error');
    }
}

// Load initial data
window.addEventListener('load', () => {
    loadMembers();
    loadTrainers();
});