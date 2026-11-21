const jwt = require("jsonwebtoken");
const bcrypt = require("bcryptjs");
const UserModel = require("../models/UserModel");

//create a account
const register = async (req, res) => {
  try {
    const { fullName, email, password } = req.body;

    if (!fullName || !email || !password) {
      return res
        .status(400)
        .send({ message: "fullName, email and password are required" });
    }

    if (UserModel.findByEmail(email)) {
      return res.status(400).send({ message: "Email already exists" });
    }

    const hash = await bcrypt.hash(password, 5);
    UserModel.create({ fullName, email, password: hash });

    res.status(200).send({ message: "Signup successful" });
  } catch (error) {
    res
      .status(500)
      .send({ message: "Something went wrong, please try again" });
  }
};

//Login here
const login = async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res
        .status(400)
        .send({ message: "email and password are required" });
    }

    const user = UserModel.findByEmail(email);
    if (!user) {
      return res.status(404).send({ message: "User not found" });
    }

    const result = await bcrypt.compare(password, user.password);
    if (!result) {
      return res.status(401).send({ message: "Login failed" });
    }

    const token = jwt.sign(
      { userId: user.id, userName: user.fullName },
      process.env.JWT_SECRET
    );

    res.status(200).send({
      message: "Login successful",
      token,
      userName: user.fullName,
      userId: String(user.id),
    });
  } catch (error) {
    console.error(error);

    res
      .status(500)
      .send({ message: "Something went wrong, please try again" });
  }
};

module.exports = { register, login };
