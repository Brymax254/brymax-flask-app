PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE user (
	id INTEGER NOT NULL, 
	username VARCHAR(100) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	role VARCHAR(20) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (username)
);
INSERT INTO user VALUES(1,'BrymaxTech','scrypt:32768:8:1$tdT9B3LezmlHz9IY$f965d0eded8510674ee04dbda6e3feb86912bd6c9b4edd3dee26a26d1e2d40d58677e440b15be2e40de392728b77ef1b652b020919f903eec6cf9758f7422983','admin');
INSERT INTO user VALUES(2,'TERRY','scrypt:32768:8:1$dgQfuFRDzhXyBi9c$04ae9abf53d7eb9cfc1b9e824086752b386bb64d0aec6d9b744beb979e3717ca6a738179539b5865748ca311ae8a6be1f191ca6f191ec7f4469201b2d4f577cb','user');
CREATE TABLE employee (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	position VARCHAR(100) NOT NULL, 
	PRIMARY KEY (id)
);
CREATE TABLE report (
	id INTEGER NOT NULL, 
	report_date DATE NOT NULL, 
	officer_name VARCHAR(100) NOT NULL, 
	farmers_registered INTEGER NOT NULL, 
	total_acres FLOAT NOT NULL, 
	staff_attendance VARCHAR(100) NOT NULL, 
	PRIMARY KEY (id)
);
INSERT INTO report VALUES(1,'2025-03-28','FRANCIS NDEGWA',2,3.0,'FRANCIS OPERATIONS');
INSERT INTO report VALUES(2,'2025-03-28','JUDY WAMBUI',1,1.0,'PATRICK DIRECTOR');
INSERT INTO report VALUES(3,'2025-03-28','FRANCIS NDEGWA',2,1.0,'OTHER ENEK OFFICIALS');
INSERT INTO report VALUES(4,'2025-03-28','CATHERINE WANJIKU',0,0.0,'NONE');
INSERT INTO report VALUES(5,'2025-03-28','FRANCIS NDEGWA',1,1.0,'NONE');
CREATE TABLE farmer (
	id INTEGER NOT NULL, 
	unique_number VARCHAR(10) NOT NULL, 
	full_name VARCHAR(100) NOT NULL, 
	county VARCHAR(50) NOT NULL, 
	subcounty VARCHAR(50) NOT NULL, 
	ward VARCHAR(50) NOT NULL, 
	location VARCHAR(50) NOT NULL, 
	phone_number VARCHAR(15) NOT NULL, 
	village VARCHAR(50) NOT NULL, 
	land_size FLOAT NOT NULL, 
	season VARCHAR(3) NOT NULL, 
	year INTEGER NOT NULL, 
	farmer_number INTEGER NOT NULL, 
	fertilizer_type VARCHAR(50), 
	kgs_issued FLOAT, 
	kgs_harvested_clean FLOAT, 
	kgs_harvested_husk FLOAT, 
	amount_received FLOAT, 
	PRIMARY KEY (id), 
	UNIQUE (unique_number), 
	UNIQUE (phone_number)
);
INSERT INTO farmer VALUES(1,'OND-2025-000001','BRYMAX','NYERI','KIENI','THEGU','THEGU','+254759234580','CHAKA',5.0,'OND',2025,1,NULL,NULL,NULL,NULL,NULL);
CREATE TABLE course (
	id INTEGER NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	description TEXT, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);
CREATE TABLE profile (
	id INTEGER NOT NULL, 
	phone VARCHAR(15), 
	address VARCHAR(255), 
	emergency_contact VARCHAR(15), 
	employee_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(employee_id) REFERENCES employee (id)
);
CREATE TABLE goal (
	id INTEGER NOT NULL, 
	description VARCHAR(255) NOT NULL, 
	progress FLOAT, 
	employee_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(employee_id) REFERENCES employee (id)
);
CREATE TABLE attendance (
	id INTEGER NOT NULL, 
	check_in DATETIME, 
	check_out DATETIME, 
	location VARCHAR(255), 
	employee_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(employee_id) REFERENCES employee (id)
);
CREATE TABLE input_distribution (
	id INTEGER NOT NULL, 
	farmer_id INTEGER NOT NULL, 
	input_type VARCHAR(50) NOT NULL, 
	date_given DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(farmer_id) REFERENCES farmer (id)
);
CREATE TABLE ploughing (
	id INTEGER NOT NULL, 
	farmer_id INTEGER NOT NULL, 
	date_ploughed DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(farmer_id) REFERENCES farmer (id)
);
CREATE TABLE harvest (
	id INTEGER NOT NULL, 
	farmer_id INTEGER NOT NULL, 
	clean_kgs FLOAT NOT NULL, 
	husk_kgs FLOAT NOT NULL, 
	date_recorded DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(farmer_id) REFERENCES farmer (id)
);
CREATE TABLE payment (
	id INTEGER NOT NULL, 
	farmer_id INTEGER NOT NULL, 
	amount_paid FLOAT NOT NULL, 
	date_paid DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(farmer_id) REFERENCES farmer (id)
);
CREATE TABLE seed (
	id INTEGER NOT NULL, 
	farmer_id INTEGER NOT NULL, 
	seed_type VARCHAR(50) NOT NULL, 
	quantity FLOAT NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(farmer_id) REFERENCES farmer (id)
);
CREATE TABLE pesticide (
	id INTEGER NOT NULL, 
	farmer_id INTEGER NOT NULL, 
	pesticide_type VARCHAR(50) NOT NULL, 
	quantity FLOAT NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(farmer_id) REFERENCES farmer (id)
);
CREATE TABLE manure (
	id INTEGER NOT NULL, 
	farmer_id INTEGER NOT NULL, 
	quantity FLOAT NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(farmer_id) REFERENCES farmer (id)
);
CREATE TABLE payroll (
	id INTEGER NOT NULL, 
	farmer_id INTEGER NOT NULL, 
	amount FLOAT NOT NULL, 
	date_created DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(farmer_id) REFERENCES farmer (id)
);
CREATE TABLE updates (
	id INTEGER NOT NULL, 
	title VARCHAR(255) NOT NULL, 
	content TEXT NOT NULL, 
	created_at DATETIME, 
	PRIMARY KEY (id)
);
INSERT INTO updates VALUES(1,'TREDDING NEWS','UP','2025-03-28 01:30:40.997546');
INSERT INTO updates VALUES(2,'farmer','farmer','2025-03-28 09:58:58.115869');
CREATE TABLE daily_reports (
	id INTEGER NOT NULL, 
	report_date DATE NOT NULL, 
	officer_name VARCHAR(120) NOT NULL, 
	farmers_registered INTEGER NOT NULL, 
	total_acres FLOAT NOT NULL, 
	tractors_in_area INTEGER, 
	acres_ploughed FLOAT, 
	staff_attendance VARCHAR(120) NOT NULL, 
	PRIMARY KEY (id)
);
INSERT INTO daily_reports VALUES(1,'2025-03-03','SYLVIA WAMUCI',1,1.0,1,2.0,'OTHER ENEK OFFICIALS');
COMMIT;
