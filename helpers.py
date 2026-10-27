# utils.py atau helpers.py

SOIL_PARAMETER_TRANSLATION = {
    # Parameter Tanah - Fisik
    'TEKSTUR': 'Tekstur Tanah',
    'KTG_TXTR': 'Kelas Tekstur',
    'BD_NILAI': 'Berat Volume (g/cm³)',
    'BD_KRIT': 'Kriteria Berat Volume',
    'DRAINASE': 'Drainase',
    'Kdl_tanah': 'Kedalaman Tanah Efektif (cm)',
    'DALAM_TNH': 'Kedalaman Tanah (cm)',
    'DALAM_KRIT': 'Kriteria Kedalaman',
    'BATUAN_NIL': 'Persentase Batuan (%)',
    'BATUAN_KRI': 'Kriteria Batuan',
    'KS_NILAI': 'Permeabilitas (cm/jam)',
    'KS_KRIT': 'Kriteria Permeabilitas',
    
    # Parameter Tanah - Kimia
    'PH_NILAI': 'pH Tanah',
    'PH_KRIT': 'Kriteria pH',
    'K_NILAI': 'Kalium (me/100g)',
    'K_KRIT': 'Kriteria Kalium',
    'N_NILAI': 'Nitrogen Total (%)',
    'N_KRUT': 'Kriteria Nitrogen',
    'P_NILAI': 'Fosfor (ppm)',
    'P_KRIT': 'Kriteria Fosfor',
    'CORG_NILAI': 'Karbon Organik (%)',
    'CORG_KRIT': 'Kriteria Karbon Organik',
    'KTK_NILAI': 'KTK (me/100g)',
    'KTK_KRIT': 'Kriteria KTK',
    'EC_NILAI': 'Konduktivitas Listrik (dS/m)',
    'EC_KRIT': 'Kriteria Salinitas',
    
    # Parameter Iklim
    'STASIUN': 'Stasiun Iklim',
    'CH_MAKS_55': 'Curah Hujan Maks (mm)',
    'CH_MIN_557': 'Curah Hujan Min (mm)',
    
    # Parameter Topografi
    'KL': 'Kemiringan Lereng (%)',
    
    # Parameter Lahan
    'GUNA_LAHAN': 'Penggunaan Lahan',
    'VEGETASI': 'Vegetasi',
    'KECAMATAN': 'Kecamatan',
    'TITIK_SAMP': 'Titik Sampel',
    
    # Hasil Analisis
    'Suai': 'Kelas Kesesuaian',
    'UNIT': 'Satuan/Kelas Lahan',
    
    # Default untuk key yang tidak dikenali
    'default': 'Parameter'
}

def translate_soil_param(key):
    """Translate soil parameter key to human-readable label."""
    return SOIL_PARAMETER_TRANSLATION.get(key, key.replace('_', ' ').title())