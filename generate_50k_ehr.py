import pandas as pd
import random

first_names = ["Rahul", "Priya", "John", "Alice", "Amit", "Neha", "Michael", "Sarah", "David", "Emily", "Rohan", "Sneha", "Vikram", "Anjali", "Kevin", "Laura", "Aarav", "Diya", "Karan", "Pooja"]
last_names = ["Gandhi", "Sharma", "Doe", "Smith", "Kumar", "Singh", "Johnson", "Williams", "Brown", "Jones", "Verma", "Patel", "Gupta", "Reddy", "Lee", "Garcia", "Joshi", "Das", "Rao", "Nair"]
genders = ["Male", "Female"]

# A large list of medically accurate symptom -> diagnosis -> medication profiles
medical_profiles = [
    {"symptom": "mild fever and cough", "diagnosis": "seasonal influenza", "medication": "Paracetamol 500mg"},
    {"symptom": "acute shortness of breath", "diagnosis": "asthma exacerbation", "medication": "Albuterol inhaler"},
    {"symptom": "ongoing migraines", "diagnosis": "tension headaches", "medication": "Ibuprofen 400mg"},
    {"symptom": "high blood pressure", "diagnosis": "hypertension", "medication": "Lisinopril 10mg"},
    {"symptom": "frequent urination and thirst", "diagnosis": "type 2 diabetes", "medication": "Metformin 500mg"},
    {"symptom": "severe head pain with aura", "diagnosis": "migraine", "medication": "Sumatriptan 50mg"},
    {"symptom": "chest heartburn and acid reflux", "diagnosis": "GERD", "medication": "Omeprazole 20mg"},
    {"symptom": "sneezing and runny nose", "diagnosis": "allergic rhinitis", "medication": "Cetirizine 10mg"},
    {"symptom": "chest pain and fever", "diagnosis": "bacterial pneumonia", "medication": "Azithromycin 250mg"},
    {"symptom": "skin rash and itching", "diagnosis": "contact dermatitis", "medication": "Hydrocortisone cream"},
    {"symptom": "fatigue and weakness", "diagnosis": "iron deficiency anemia", "medication": "Iron supplements 65mg"},
    {"symptom": "joint pain and swelling", "diagnosis": "rheumatoid arthritis", "medication": "Methotrexate 15mg"},
    {"symptom": "difficulty sleeping", "diagnosis": "insomnia", "medication": "Melatonin 5mg"},
    {"symptom": "sore throat and pain swallowing", "diagnosis": "strep throat", "medication": "Penicillin V 500mg"},
    {"symptom": "sharp pain in lower right abdomen", "diagnosis": "appendicitis", "medication": "Surgical appendectomy scheduled"},
    {"symptom": "red, itchy eye with discharge", "diagnosis": "conjunctivitis", "medication": "Erythromycin ophthalmic ointment"},
    {"symptom": "faintness, palpitations, anxiety", "diagnosis": "panic disorder", "medication": "Sertraline 50mg"},
    {"symptom": "burning sensation while urinating", "diagnosis": "urinary tract infection", "medication": "Nitrofurantoin 100mg"},
    {"symptom": "persistent depressed mood", "diagnosis": "major depressive disorder", "medication": "Fluoxetine 20mg"},
    {"symptom": "lower back pain radiating to leg", "diagnosis": "sciatica", "medication": "Naproxen 500mg"},
    {"symptom": "ear pain and muffled hearing", "diagnosis": "otitis media", "medication": "Amoxicillin 875mg"},
    {"symptom": "stomach pain and diarrhea", "diagnosis": "gastroenteritis", "medication": "Oral rehydration salts & Loperamide"},
    {"symptom": "itchy scaly patches on scalp", "diagnosis": "psoriasis", "medication": "Betamethasone topical"},
    {"symptom": "blurred vision and spots", "diagnosis": "diabetic retinopathy", "medication": "Laser photo-coagulation therapy"},
    {"symptom": "dizziness and loss of balance", "diagnosis": "vertigo", "medication": "Meclizine 25mg"},
    {"symptom": "hair loss in patches", "diagnosis": "alopecia areata", "medication": "Minoxidil 5%"},
    {"symptom": "numbness in hands and feet", "diagnosis": "peripheral neuropathy", "medication": "Gabapentin 300mg"},
    {"symptom": "severe abdominal cramps and bloating", "diagnosis": "irritable bowel syndrome", "medication": "Dicyclomine 20mg"}
]

records = []
for i in range(1001, 51001):
    fname = random.choice(first_names)
    lname = random.choice(last_names)
    age = random.randint(18, 90)
    gender = random.choice(genders)
    
    # Pick one mathematically accurate diagnosis profile
    profile = random.choice(medical_profiles)
    
    ehr_text = f"Patient presented with {profile['symptom']}. Tests run. Diagnosed with {profile['diagnosis']}. Prescribed {profile['medication']}."
    
    records.append({
        "patient_id": str(i),
        "name": f"{fname} {lname}",
        "age": age,
        "gender": gender,
        "ehr_text": ehr_text
    })

df = pd.DataFrame(records)
df.to_csv("data/ehr_database.csv", index=False)
print("Successfully generated 50,000 accurate and varied records in data/ehr_database.csv")
