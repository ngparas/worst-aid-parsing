Vue.component('chat-item', {
    props: ['chat'],
    template: `
        <div v-if="chat.isUser" class="row">
          <div class="col-sm-4"></div>
          <div class="col-sm-8">
        <div class="panel panel-info" style="text-align: right">
        <div class="panel-heading">
        <h3 class="panel-title">{{ chat.text }}</h3>
    </div>
    </div>
          </div>
        </div>
        <div v-else class="row">
          <div class="col-sm-8">
            <div class="panel panel-success" style="text-align: left">
        <div class="panel-heading">
        <h3 class="panel-title">{{ chat.text }}</h3>
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
                this.addMessage(msgObj);


            if (this.procedureIndex === null) {
                // We don't have a graph loaded yet, get one
                this.getProcedure(this.userText);
                // should probably have done this before but whatever
                msgObj.textClass = 'graph';
                msgObj.textClassValue = 'graph';
                this.messageList[this.messageList.length - 1].textClass = 'graph';
                this.messageList[this.messageList.length - 1].textClassValue = 'graph';
            }

            switch(msgObj.textClass){
                case 'nav':
                    if (msgObj.textClassValue == 'next') {
                        // TODO : check bounds
                        this.procedureIndex += 1;
                        this.messageList.push({"text": "Pretend I advanced the Graph"})
                        break;
                    } else if (msgObj.textClassValue == 'prev') {
                        // TODO : check bounds
                        this.procedureIndex -= 1;
                        this.messageList.push({"text": "Pretend I moved back along the Graph"})
                        break;
                    } else {
                        // this.procedureIndex doesn't change
                        this.messageList.push({"text": "I'm going to stay here in the Graph"})
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
                    console.log('asdf')
                    break;

            }

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

        getProcedure: function(message) {
            this.$http.get('/procedures?query='+message).then(response => {

                // get body data
                this.messageList.push({
                    "text": "I can help with " + toTitleCase(response.body.key.replace(/-/g, " ")),
                    "isUser": false
                });
                this.procedureGraph = response.body.graph;
                this.procedureIndex = 0

            }, response => {
                // error callback
                this.messageList.push({
                    "text": "Something went wrong, can you try again?",
                    "isUser": false
                });
            });
        }
    }
})
