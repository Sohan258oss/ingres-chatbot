# Backend/data_manager.py

KNOWLEDGE_BASE = {
    "groundwater": [
        "Groundwater is water that has found its way down from the Earth’s surface into the cracks and spaces in soil, sand and rock.",
        "The largest use for groundwater is to irrigate crops."
    ],
    "extraction": [
        "Ground water extraction or overexploitation is when the average extraction rate from aquifers is greater than the average recharge rate.",
        "Over-extraction leads to declining groundwater levels, land subsidence, reduced water quality, and ecological damage."
    ],
    "recharge": [
        "Recharge is the process by which rainfall or surface water replenishes underground aquifers."
    ],
    "over-exploited": [
        "An over-exploited region extracts more groundwater than it naturally recharges, leading to long-term depletion."
    ],
    "safe": [
        "A 'Safe' category means groundwater extraction is below 70% of available recharge capacity."
    ],
    "critical": [
        "A 'Critical' category indicates extraction is between 90% and 100% of recharge capacity."
    ],
    "stage": [
        "Stage of Extraction is the percentage ratio of annual groundwater draft to annual extractable groundwater resource."
    ],
    "aquifer": [
        "An aquifer is an underground layer of water-bearing permeable rock, gravel, sand, or silt from which groundwater can be extracted.",
        "Aquifers act as natural reservoirs; their permeability determines how easily water moves through them."
    ],
    "borewell": [
        "A borewell is a deep, narrow hole drilled into the ground to access groundwater from deep aquifers."
    ],
    "watershed": [
        "A watershed is an area of land where all falling water drains to a common outlet like a river or lake."
    ],
    "salinity": [
        "Salinity is the concentration of dissolved salts in water, which can make groundwater unsuitable for drinking or irrigation."
    ],
    "master plan": [
        "The Master Plan for Artificial Recharge to Groundwater-2020 aims to construct 1.42 crore rainwater harvesting structures."
    ],
    "gujarat salinity": [
        "Coastal Gujarat faces seawater intrusion due to over-pumping, increasing groundwater salinity."
    ],
    "paddy water": [
        "Rice (paddy) is water-intensive, requiring 3,000 to 5,000 liters of water to produce 1 kg of grain."
    ],
    "sugarcane": [
        "Sugarcane is a high water-consuming crop contributing to groundwater depletion in states like Maharashtra and UP."
    ],
    "millets": [
        "Millets are climate-smart crops that require significantly less water than rice or wheat."
    ],
    "atal bhujal yojana": [
        "Atal Bhujal Yojana (ATAL JAL) is a scheme for sustainable groundwater management with community participation."
    ],
    "cgwb": [
        "The Central Ground Water Board (CGWB) is India's apex organization for groundwater management and monitoring."
    ],
    "pmksy": [
        "Pradhan Mantri Krishi Sinchayee Yojana (PMKSY) focuses on 'Har Khet Ko Pani' and 'Per Drop More Crop'."
    ],
    "drip irrigation": [
        "Drip irrigation delivers water directly to roots, saving 40-70% water compared to traditional methods."
    ],
    "arsenic": [
        "Arsenic contamination is a major health concern in the Ganga-Brahmaputra plains, including West Bengal and Bihar."
    ],
    "fluoride": [
        "Excessive fluoride in groundwater causes dental and skeletal fluorosis, common in Rajasthan and Telangana."
    ],
    "nitrate": [
        "Nitrate pollution often results from excessive fertilizer use and improper sewage disposal."
    ],
    "jal shakti abhiyan": [
        "Jal Shakti Abhiyan is a national campaign for water conservation and security in India."
    ],
    "national aquifer mapping": [
        "The NAQUIM program aims to delineate and characterize aquifers for sustainable management."
    ],
    "virtual water": [
        "Virtual water is the hidden volume of water used to produce food or commodities that are traded."
    ],
    "over-pumping": [
        "Over-pumping occurs when withdrawal exceeds recharge, causing water tables to drop."
    ],
    "seawater intrusion": [
        "Seawater intrusion happens in coastal areas when over-extraction causes salt water to flow into freshwater aquifers."
    ],
    "check dam": [
        "A check dam is a small structure built across a waterway to reduce water velocity and promote infiltration."
    ],
    "percolation tank": [
        "Percolation tanks are surface bodies designed to submerge permeable land and recharge groundwater."
    ],
    "dug well": [
        "Dug wells are shallow, wide-diameter wells excavated to reach the upper water table."
    ],
    "greywater": [
        "Greywater is gently used wastewater from sinks and showers that can be recycled for gardening."
    ],
    "blackwater": [
        "Blackwater is wastewater from toilets containing pathogens and requires intensive treatment."
    ],
    "infiltration": [
        "Infiltration is the process by which water on the ground surface enters the soil."
    ],
    "transpiration": [
        "Transpiration is the release of water vapor from plant leaves into the atmosphere."
    ],
    "evapotranspiration": [
        "Evapotranspiration is the combined loss of water from soil evaporation and plant transpiration."
    ],
    "water table": [
        "The water table is the upper boundary of the zone of saturation where ground is fully soaked with water."
    ],
    "confined aquifer": [
        "A confined aquifer is trapped between impermeable layers and is often under pressure."
    ],
    "unconfined aquifer": [
        "An unconfined aquifer has a water table that is open to the atmosphere and can rise or fall freely."
    ],
    "hydrogeology": [
        "Hydrogeology is the study of the distribution and movement of groundwater in soil and rocks."
    ],
    "specific yield": [
        "Specific yield is the amount of water that a saturated rock or soil will yield by gravity."
    ],
    "permeability": [
        "Permeability is the measure of a material's ability to transmit fluids through connected pores."
    ],
    "porosity": [
        "Porosity is the percentage of void space in a rock or soil that can hold water."
    ],
    "drawdown": [
        "Drawdown is the drop in water level in a well caused by pumping."
    ],
    "cone of depression": [
        "A cone of depression forms around a pumping well as water is drawn from the surrounding aquifer."
    ],
    "baseflow": [
        "Baseflow is the portion of streamflow that comes from groundwater seepage."
    ],
    "catchment area": [
        "A catchment area is the land area where rainfall collects and drains into a specific water body."
    ],
    "siltation": [
        "Siltation is the accumulation of fine mineral particles that can clog recharge structures."
    ],
    "desalination": [
        "Desalination is the process of removing salts and minerals from saline water to make it usable."
    ],
    "fecal coliform": [
        "Fecal coliform bacteria indicate contamination of water by human or animal waste."
    ],
    "hard water": [
        "Hard water contains high levels of dissolved minerals like calcium and magnesium."
    ],
    "soft water": [
        "Soft water has low mineral concentrations, making it better for certain domestic uses."
    ],
    "turbidity": [
        "Turbidity is the measure of water cloudiness caused by suspended particles."
    ],
    "ph value": [
        "The pH value measures how acidic or basic water is on a scale of 0 to 14."
    ],
    "tds": [
        "Total Dissolved Solids (TDS) is the combined content of all inorganic and organic substances in water."
    ],
    "dissolved oxygen": [
        "Dissolved oxygen (DO) is the amount of oxygen gas available in water for aquatic life."
    ],
}

CONTAMINANT_DATA = {
    "rajasthan": ["Fluoride", "Nitrate"],
    "punjab": ["Nitrate", "Arsenic"],
    "haryana": ["Fluoride", "Nitrate"],
    "west bengal": ["Arsenic", "Fluoride"],
    "bihar": ["Arsenic", "Iron"],
    "uttar pradesh": ["Fluoride", "Arsenic"],
    "karnataka": ["Fluoride", "Nitrate"],
    "tamil nadu": ["Fluoride", "Salinity"],
    "gujarat": ["Salinity", "Fluoride"],
    "andhra pradesh": ["Fluoride"],
    "delhi": ["Nitrate", "Fluoride"],
    "kolar": ["Fluoride"],
    "bangalore": ["Nitrate"],
    "tumkur": ["Fluoride"],
    "chikkaballapura": ["Fluoride"],
    "raichur": ["Arsenic"],
    "gulbarga": ["Fluoride"]
}

WHY_MAP = {
    "punjab": "High dependence on groundwater for water-intensive crops like paddy and wheat; subsidized electricity leads to over-pumping.",
    "haryana": "Intensive agricultural practices and high irrigation demand for cereal crops beyond natural recharge levels.",
    "delhi": "Massive population density, rapid urbanization, and high concretization preventing rainwater from recharging aquifers.",
    "uttar pradesh": "Heavy agricultural extraction in western districts for sugarcane; industrial pollution in areas like Kanpur (tanneries).",
    "rajasthan": "Arid climate, extremely low rainfall, and high evaporation rates; historic reliance on deep fossil water.",
    "gujarat": "Industrial demand and high salinity ingress in coastal areas; intensive irrigation in districts like Mehsana.",
    "maharashtra": "Hard rock (Basalt) terrain with low storage capacity; over-extraction for sugarcane in the Marathwada/Vidarbha belts.",
    "karnataka": "Hard rock terrain (Deccan Trap) with low storage; high borewell density for IT hubs and agriculture.",
    "tamil nadu": "Over-reliance on groundwater due to surface water scarcity and frequent failures of the monsoon.",
    "bengaluru": "Rapid expansion into peripheral zones without piped water; over-reliance on private tankers and deep borewells.",
    "chennai": "Coastal location leading to seawater intrusion; high domestic demand following reservoir failures.",
    "gurugram": "Extremely high construction demand and deep extraction for high-rise residential complexes.",
    "jaipur": "Semi-arid climate coupled with tourism and luxury residential demand exceeding replenishment.",
    "odisha": "Coastal districts face salinity ingress due to proximity to the sea, while inland areas have limited storage in hard rock aquifers.",
    "bihar": "High levels of arsenic and fluoride contamination in certain belts; seasonal flooding can also impact groundwater quality.",
    "assam": "Despite abundant rainfall, certain regions face high iron and arsenic content in shallow aquifers.",
    "kerala": "Laterite soil has high permeability but low storage, leading to seasonal water scarcity despite high annual rainfall."
}

TIPS = {
    "conservation": "To conserve groundwater: 1. Install rainwater harvesting systems. 2. Use drip or sprinkler irrigation. 3. Recycle greywater for gardening. 4. Fix leaks promptly.",
    "harvesting": "Rainwater harvesting involves collecting and storing rainwater from rooftops or ground surfaces to recharge aquifers or for direct use.",
    "farming": "Sustainable farming tips: 1. Adopt crop rotation. 2. Grow less water-intensive crops like millets. 3. Use mulch to retain soil moisture.",
    "pollution": "Prevent pollution by: 1. Reducing fertilizer and pesticide use. 2. Proper disposal of hazardous waste. 3. Ensuring septic systems are well-maintained.",
    "crop choice": "Switch from water-intensive crops like paddy to millets or pulses in water-stressed regions.",
    "mulching": "Use organic mulch in fields to reduce evaporation from the soil surface.",
    "smart irrigation": "Adopt sensors and automated systems to provide water to crops only when needed.",
    "community participation": "Form Water User Associations to collectively manage and monitor groundwater usage in villages.",
    "well recharging": "Redirect surplus monsoon runoff into defunct dug wells to recharge local aquifers.",
}

LAYERED_METADATA = {
    "groundwater": {
        "why": "It's the primary source of water for half of the world's population and essential for agriculture.",
        "impact": "Depletion threatens food security and domestic water supply.",
        "tip": "Reduce wastage in households and adopt rainwater harvesting."
    },
    "aquifer": {
        "why": "Acts as a natural underground reservoir for storing water.",
        "impact": "Over-extraction can cause land subsidence and permanent loss of storage capacity.",
        "tip": "Protect recharge areas from urban sprawl and pollution."
    },
    "recharge": {
        "why": "It's the natural process that keeps our groundwater levels stable.",
        "impact": "Low recharge leads to dropping water tables and drying wells.",
        "tip": "Use check dams and percolation tanks to enhance natural recharge."
    },
    "extraction": {
        "why": "High extraction rates indicate we are using water faster than nature can replenish it.",
        "impact": "Leads to water stress, saline ingress in coastal areas, and higher pumping costs.",
        "tip": "Switch to water-efficient irrigation methods like drip or sprinklers."
    }
}
