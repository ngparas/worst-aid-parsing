Vue.component('chat-item', {
    props: ['chat'],
    template: `
        <div v-if="chat.isUser" class="row">
          <div class="col-sm-4"></div>
          <div class="col-sm-8">
            <p style="text-align: right" class="lead">{{ chat.text }}</p>
          </div>
        </div>
        <div v-else class="row">
          <div class="col-sm-8">
            <p style="text-align: left" class="lead">{{ chat.text }}</p>
          </div>
          <div class="col-sm-4"></div>
        </div>
        `
})

var mainapp = new Vue({
    el: '#mainapp',
    data: {
        userText: "",
        messageList: [],
        procedureGraph: [],
        procedureIndex: null
    },
    methods: {

        addMessage: function() {
            this.messageList.push({"text": this.userText,
                                   "isUser": true});
            this.getProcedure(this.userText);
            this.userText = "";
        },

        getProcedure: function(message) {
            this.$http.get('/procedures?query='+message).then(response => {

                // get body data
                this.messageList.push({"text": response.body.key});
                this.procedureGraph = response.body.graph;

            }, response => {
                // error callback
                this.messageList.push({"text": "Something went wrong, can you try again?"});
            });
        }


    }

})
