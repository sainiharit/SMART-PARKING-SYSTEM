const functions = require('firebase-functions');
const admin = require('firebase-admin');
const nodemailer = require("nodemailer");
admin.initializeApp({
    credential: admin.credential.applicationDefault(),
  	databaseURL:"############",}
);

const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
        user: 'yoyorahulem2@gmail.com',
        pass: '#############'
    }
});


const db = admin.database();

// const account_sid = '#########';
// const auth_token = '##########';

// const client = require('twilio')(account_sid,auth_token);

// exports.detectSendMessage = functions.database.ref('/users/{userPushId}/phone')
//         .onCreate((snapshot,context) => {
//             let phone = snapshot.val();
//                 if(phone!==null) {
//                 phone = '+91'+ phone;
//                 client.messages
//                     .create({body: 'Hi there!', from: '+17724130748', to: `${phone}`})
//                     .then(message => console.log(message.sid)).catch(err=>console.log(err));
//                 }
// });

exports.detectSlotChange = functions.database.ref('/slots')
                        .onUpdate((change,context)=>{
                            let before = change.before.val();
                            let after = change.after.val();
                            let slotChanged;
                            //console.log(before[0]);
                            for (let i = 0, len = before.length; i < len; i++) {
                                if (before[i].occupied !== after[i].occupied) {
                                    slotChanged = i;
                                }
                            }
                            if(slotChanged===null) return;
                            if(after[slotChanged].occupied===0) {
                                //Car Parked
                                //save timestamp
                                db.ref(`slots/${slotChanged}`).once('value', (snapshot)=> {
                                    const slot = snapshot;
                                    if(slot.child('user').exists()) {
                                        db.ref('slots').child(`${slotChanged}`).update({parkingtime:Date.now()});
                                    } else {
                                        const mailOptions = {
                                            from: "Haywire", // sender address
                                            to: `parv0697@gmail.com`, // list of receivers
                                            subject: "Fine Alert", // Subject line
                                            html: `<p> There is a unautherized car at slot no. ${ slotChanged } </p>` 
                                        };
                                        transporter.sendMail(mailOptions, function (err, info) {
                                            if(err)
                                            {
                                              console.log(err);
                                            }
                                        });
                                    }
                                });
                                
                                //Send Email regarding that the car has been parked
                            } else if(after[slotChanged].occupied===1){
                                // Car Taken Out
                                //Send Email that car has been taken out and send the amount with it 
                                const currenttime = Date.now();
                                db.ref(`slots/${slotChanged}`).once('value',(snapshot)=>{const obj = snapshot.val()
                                    const duration = currenttime - obj.parkingtime;
                                    const mins = duration / 360;
                                    const amount = mins;
                                    const user = obj.user;
                                    db.ref(`users/${user}`).once('value',(snapshot)=>{
                                        const obj = snapshot.val();
                                        const email = obj.email;
                                        const mailOptions = {
                                            from: "Haywire", // sender address
                                            to: `${email}`, // list of receivers
                                            subject: "Vehicle taken out", // Subject line
                                            html: `<p> Thank you for using our service. The amount is ${amount} </p>` 
                                        };
                                        transporter.sendMail(mailOptions, function (err, info) {
                                            if(err)
                                            {
                                              console.log(err);
                                            }
                                        });
                                    });
                                    
                                });
                                
                            }
                            return;
                        });

// // Create and Deploy Your First Cloud Functions
// // https://firebase.google.com/docs/functions/write-firebase-functions
//
// exports.helloWorld = functions.https.onRequest((request, response) => {
//  response.send("Hello from Firebase!");
// });