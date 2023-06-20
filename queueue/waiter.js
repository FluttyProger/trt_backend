const Queue = require('bee-queue');

const options = {
    isWorker: false,
    sendEvents: true,
    redis: {
        host: process.env.DB_HOST,
        port: process.env.DB_PORT,
        password: process.env.DB_PASS,
    }
}

const cookQueue = new Queue('cook', options);


const placeOrder = async (order) => {
        var jobb = await cookQueue.createJob(order).save();
        jobb.on('failed', (err) => {
                console.log(`Job failed with error ${err.message}`);
        });

        return jobb;
};

cookQueue.on("succeeded", (job) => {
    // Notify the client via push notification, web socket or email etc.
    console.log(`  ${job.data.qty}x ${job.data.dish} ready to be served 😋`);
});

cookQueue.on('failed', (err) => {
  console.log(`Job failed with error ${err.message}`);
});

cookQueue.on('job succeeded', (jobId, result) => {
  console.log(`Job ${jobId} succeeded with result: ${result}`);
});

const getOrderStatus = (orderId) => {
    return cookQueue.getJob(orderId).then((job) => {
        return {
            progress: job.progress,
            status: job.status,
            order: job.data
        };
    });
}

module.exports = {
    placeOrder: placeOrder,
    getStatus: getOrderStatus
};