parking_data = {
    "AB3": {
        "vehicle_type": "2W",
        "spaces": {
            "S1": True,
            "S2": False,
            "S3": True,
            "S4": True,
            "S5": False
        }
    },
    "AB2": {
        "vehicle_type": "2W",
        "spaces": {
            "S1": False,
            "S2": False,
            "S3": True
        }
    },
    "AB1": {
        "vehicle_type": "4W",
        "spaces": {
            "S1": True,
            "S2": True,
            "S3": False
        }
    },
    "Student Parking 1": {
        "vehicle_type": "Mixed",
        "spaces": {
            "S1": True,
            "S2": False,
            "S3": True,
            "S4": True
        }
    }
}
events_data = [
    {"title": "AI Guest Lecture", "location": "MG Auditorium", "time": "10:00 AM"},
    {"title": "Anime Club Meeting", "location": "Gazebo", "time": "4:00 PM"},
]
static_data = [
    {
        "building": "AB1",
        "type": "Academic Block",
        "description": "This is AB1. This is an 8 floor block mainly for first year. It contains Netaji Auditorium"
    },
    {
        "building": "AB2",
        "type": "Academic Block",
        "description": "This is AB2. This is a seven floor block where mostly second years study"
    },
    {
        "building": "AB3",
        "type": "Academic Block",
        "description": "This is AB3. For third years and second years. Has a canteen on ground floor."
    },
    {
        "building": "MG Auditorium",
        "type": "Auditorium",
        "description": "Main auditorium used for events."
    },
    {
        "building": "Gazebo",
        "type":"Food Court",
        "description":"Gazebo is the biggest hangout place for VIT students. It comprises of 4 shops, 3 for food and 1 for drinks. In the mood for shawarma or chaat? Shop c1 is the place for you. Momos, sandwiches, wraps, pasta, burger? C2. Something more desi, like parotta, biriyani or a goli soda? C3, also known as Dakshin. Feeling thirsty? Lassi house is the place for you."
    },
    {
        "building": "North Square",
        "type": "Food Court",
        "description": "A nice, cozy hangout spot after a day of classes, North Square consists of 4 shops serving everything from chaat, rolls, shawarma and noodles, to ice tea, brownies, and french fries."
    },
    {
        "building":"A-block men's hostel.",
        "type":"Boy's hostel",
        "description":"The oldest hostel of VIT. Consists of 16 floors with 50 rooms per floor. Has 2 bed, 3 bed, 4 bed, 6 bed and 8 bed rooms, both air conditioned and non air conditioned. Boasts a badminton court on the ground floor, a gym on the first floor, and a table tennis court."
    },
    {
        "building":"C-block hostel.",
        "type":"Co-ed hostel",
        "description":"This is a block shared by boys and girls. Movies are screened regularly in front of this block. Has 2 bed, 3 bed, 4 bed and 6 beds, both AC and non AC. Indoor badminton court and gym"
    },
    {
        "building" : "E-block men's hostel.",
        "type" : "Boy's hostel",
        "description":"The most recently constructed hostel. 17 floors with 50 rooms per floor. All air conditioned rooms. Outdoor gym as well as indoor gym and indoor laundry."
    },
    {
        "building" : "Health Center",
        "type" : "Clinic",
        "description" : "Open 24x7. Has ambulances that ply regularly to Chettinad hospital for more advanced treatment. Houses 2 refrigerators for storing medicine, including any a student might wish to deposit. Simple medicines like ORS sachets, paracetamol and antibiotics are provided free of cost."
    }
]
laundry_data = [
    {"Bag Number": "D1-101", "done": False},
    {"Bag Number": "E-122", "done": True},
    {"Bag Number": "C-203", "done": False},
    {"Bag Number": "B-162", "done": True},
    {"Bag Number": "D2-155", "done": False},
]