const Queue = require('bee-queue');
const axios = require('axios');
const banana = require('@banana-dev/banana-dev');
const { initializeApp, cert } = require('firebase-admin/app');
const { getStorage } = require('firebase-admin/storage');
const { getDatabase } = require('firebase-admin/database');
var serviceAccount = require("./serviceAccountKey.json");
const admin = require('firebase-admin');
admin.initializeApp({
  projectId: serviceAccount.project_id,
  credential: admin.credential.cert(serviceAccount),
  databaseURL: "https://crucial-sphinx-304212-default-rtdb.europe-west1.firebasedatabase.app",
  storageBucket: "crucial-sphinx-304212.appspot.com"
});

const options = {
    redis: {
        host: process.env.DB_HOST,
        port: process.env.DB_PORT,
        password: process.env.DB_PASS,
    }
}

const cookQueue = new Queue('cook', options);
const db = getDatabase();

cookQueue.process(1, async (job, done) => {
//    let qty = job.data.qty;
//    let cooked = 0;
try {

    var url = 'http://127.0.0.1:8000';
    var out = await axios.post(url, JSON.parse(job.data.jsn));

    const bucket = getStorage().bucket();
    const ref = db.ref("Users/"+job.data.userid+"/Images/"+job.data.jobid);
    const reff = db.ref("UserImages/"+job.data.userid+":"+job.data.jobid);
//    console.log(out);
    const imageBuffer = Buffer.from(out.data.images[0], 'base64');
    const jsondata = JSON.parse(out.data.info);
    const imageByteArray = new Uint8Array(imageBuffer);
    const file = bucket.file("images/"+job.data.userid+"/"+job.data.jobid+".png");
    const options = { resumable: false, metadata: { contentType: "image/png" } }
    //console.log(jsondata);
    const nsfww = jsondata.styles[0];

    await file.save(imageByteArray, options);
    reff.update({nsfw:nsfww});
    ref.update({Status: "done", nsfw:nsfww});
//      console.log("eshkere");
        done();

} catch(e) {

  console.log('Ошибка ' + e.name + ":" + e.message + "\n" + e.stack); // (3) <-
});