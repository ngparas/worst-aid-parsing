Vue.component('chat-item', {
    props: ['chat'],
    template: `
        <div v-if="chat.isUser" class="row">
          <div class="col-sm-4"></div>
          <div class="col-sm-8">
        <div class="panel panel-info" style="text-align: right">
        <div class="panel-heading">
        <h3 class="panel-title" v-html="chat.text"></h3>
    </div>
    </div>
          </div>
        </div>
        <div v-else class="row">
          <div class="col-sm-8">
            <div class="panel panel-success" style="text-align: left">
        <div class="panel-heading">
        <h3 class="panel-title" v-html="chat.text"></h3>
    </div>
</div>
          </div>
          <div class="col-sm-4"></div>
        </div>
        `
})

// copy pasta credit: http://stackoverflow.com/a/196991
function toTitleCase(str)
{
    return str.replace(/\w\S*/g, function(txt){
        return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    });
}

var mainapp = new Vue({
    el: '#mainapp',
    data: {
        userText: "",
        messageList: [{"text": "How can I help?"}],
        procedureGraph: [],
        procedureIndex: null,
        innerIndex: null,
    },
    methods: {

        submitMessage: function() {
            // need to classify message
            this.$http.get('/classifier?query='+this.userText).then(response => {
                // get body data
                var msgObj = {'text': this.userText,
                              'isUser': true}
                msgObj.textClass = response.body.textClass;
                msgObj.textClassValue = response.body.value;

                this.messageList.push(msgObj);
                this.setProcedureIfNecessary(msgObj).then(msgObj => {
                    this.userText = "";

                    switch(msgObj.textClass){
                        case 'nav':
                            if (msgObj.textClassValue == 'next') {
                                if(this.innerIndex == null || (this.innerIndex + 1) >= this.procedureGraph[this.procedureIndex].substeps.length) {
                                    this.procedureIndex += 1;
                                    this.innerIndex = null;
                                }
                                else {
                                    this.innerIndex += 1;
                                }
                                // this.messageList.push({"text": "Pretend I advanced the Graph"})
                                this.renderStep();
                                break;
                            } else if (msgObj.textClassValue == 'prev') {
                                // TODO : Goes back the previous main step instead of substep
                                this.procedureIndex -= 1;
                                this.innerIndex = null;
                                // this.messageList.push({"text": "Pretend I moved back along the Graph"})
                                this.renderStep();
                                break;
                            } else {
                                // this.procedureIndex doesn't change
                                this.messageList.push({"text": "I'm going to stay here in the Graph"})
                                this.renderStep();
                                break;
                            }
                            break;
                            // some other stuff
                        case 'question':
                            // some other stuff
                            this.messageList.push({"text": "You asked a question, let's pretend I responded"})
                            break;
                        case 'answer':
                            // some more other stuff
                            if (msgObj.textClassValue == true) {
                                this.messageList.push({"text": "I heard you say yes"})
                                break;
                            } else {
                                this.messageList.push({"text": "I heard you say no"})
                                break;
                            }
                                break;
                        default:
                            // get here from the 'graph' type, so start at 0
                            // this.messageList.push({"text": "<b>Hi</b> world."});
                            this.renderStep();
                            break;

                    }
                }, err => {
                    console.error('Error setting procedure graph.');
                });

            }, response => {
                // error callback
                this.messageList.push({
                    "text": "Something went wrong, can you try again?",
                    "isUser": false
                });
            });

        },

        addMessage: function(messageObj) {
            this.messageList.push(messageObj);
            this.userText = "";
        },

        renderStep: function() {
            if(this.procedureIndex < 0) {
                this.messageList.push({"text": "Beginning of Instructions"});
                this.procedureIndex = -1;
            }
            else if(this.procedureIndex >= Object.keys(this.procedureGraph).length) {
                this.messageList.push({"text": "End of Instructions."})
                this.procedureIndex = Object.keys(this.procedureGraph).length;
            }
            else {
                let step = this.procedureGraph[this.procedureIndex];
                let msg = '';
                switch(step.type) {
                    case '911-conditional':
                        msg = step.substeps.map(substep => "<li>"+substep.text+"</li>").join('');
                        this.messageList.push({"text": step.text+"<br>"+"<ul>"+msg+"</ul>"});
                        break;
                    case 'doctor-conditional':
                        msg = step.substeps.map(substep => "<li>"+substep.text+"</li>").join('');
                        this.messageList.push({"text": step.text+"<br>"+"<ul>"+msg+"</ul>"});
                        break;
                    default:
                        if(this.innerIndex == null) {
                            this.messageList.push({"text": step.text})
                            this.innerIndex = 0;
                        }
                        this.messageList.push({"text": step.substeps[this.innerIndex].text});
                }
            }
        },

        setProcedureIfNecessary: function(msgObj) {
            let promise = new Promise((resolve, reject) => {
                if (this.procedureIndex === null) {
                    // We don't have a graph loaded yet, get one
                    this.getProcedure(this.userText).then(response => {
                        // get body data
                        if(response.body.key === 'none'){
                            this.messageList.push({
                                "text": "I'm sorry, I don't recognize that. Please try again.",
                                "isUser": false
                            });
                        }
                        else{
                                this.messageList.push({
                                "text": "I can help with " + toTitleCase(response.body.key.replace(/-/g, " ")),
                                "isUser": false
                            });
                            this.procedureGraph = response.body.graph;
                            this.procedureIndex = 0

                            // Set graph
                            msgObj.textClass = 'graph';
                            msgObj.textClassValue = 'graph';
                            this.messageList[this.messageList.length - 1].textClass = 'graph';
                            this.messageList[this.messageList.length - 1].textClassValue = 'graph';
                            resolve(msgObj);
                        }
                    }, err => {
                        // error callback
                        this.messageList.push({
                            "text": "Something went wrong, can you try again?",
                            "isUser": false
                        });
                        reject();
                    });
                }
                else {
                  resolve(msgObj);
                }
            });
            return promise;
        },

        getProcedure: function(message) {
            return this.$http.get('/procedures?query='+message);
        }
    }
})
