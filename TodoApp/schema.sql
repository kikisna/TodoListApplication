CREATE TABLE User (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE Task (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    deadline DATETIME,
    task_type VARCHAR(255),
    creation_time DATETIME,
    done_time DATETIME,
    status ENUM('Todo', 'Done') NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(id)
);
