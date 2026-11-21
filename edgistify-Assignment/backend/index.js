const express = require("express");
const cors = require("cors");
const { db, PORT } = require("./config/db");
const { userRouter } = require("./routes/UserRoutes");
const { productRouter } = require("./routes/ProductRoutes");
const { cartRouter } = require("./routes/CartRoutes");
const { orderRouter } = require("./routes/OrderRoutes");

const app = express();

app.use(express.json());
app.use(cors());

app.get("/", (req, res) => {
    res.json({ message: "Server is running!"});
});

app.use("/api/users", userRouter);
app.use("/api/products", productRouter);
app.use('/api/cart', cartRouter); 
app.use("/api/orders", orderRouter); 

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`SQLite database: ${db.name}`);
    console.log(`Listening on PORT: ${PORT}`);
  });
}

module.exports = app;