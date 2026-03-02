import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

DRUG_CLASSES = ['ACE_Inhibitor', 'ARB', 'Calcium_Channel_Blocker', 'Diuretic', 
                'Beta_Blocker', 'Alpha_Blocker', 'Central_Acting']
NUM_DRUGS = len(DRUG_CLASSES)

DRUG_NAMES = {
    'ACE_Inhibitor': 'ACE Inhibitor (Lisinopril)',
    'ARB': 'ARB (Losartan)',
    'Calcium_Channel_Blocker': 'Calcium Channel Blocker (Amlodipine)',
    'Diuretic': 'Diuretic (Hydrochlorothiazide)',
    'Beta_Blocker': 'Beta Blocker (Metoprolol)',
    'Alpha_Blocker': 'Alpha Blocker (Doxazosin)',
    'Central_Acting': 'Central Acting Agent (Clonidine)'
}
RANDOM_STATE = 42
