var mainapp = new Vue({
    el: '#mainapp',
    data: {
        userText: "",
        messageList: []
    },
    methods: {

        addMessage: function() {
            this.messageList.push({"text": this.userText})
            this.userText = ""
        }


    }

})

Vue.component('chat-item', {
    props: ['chat'],
    template: '<p class="lead">{{ chat.text }}</p>'
})
