import time
import requests
import re
import streamlit as st

def get_chat_id(yt_url):
    '''
    https://developers.google.com/youtube/v3/docs/videos/list?hl=ja
    '''
    video_id = yt_url.replace('https://www.youtube.com/watch?v=', '').replace('https://www.youtube.com/live/', '')
    print('video_id : ', video_id)

    url    = 'https://www.googleapis.com/youtube/v3/videos'
    params = {'key': YT_API_KEY, 'id': video_id, 'part': 'liveStreamingDetails'}
    data   = requests.get(url, params=params).json()

    try:
        liveStreamingDetails = data['items'][0]['liveStreamingDetails']
        if 'activeLiveChatId' in liveStreamingDetails.keys():
            chat_id = liveStreamingDetails['activeLiveChatId']
            st.write('success connecting.')
        else:
            chat_id = None
            st.write('Not live now.')
    except:
        chat_id = None
        st.write('Not exist.')

    return chat_id

def get_chat(chat_id, pageToken):
    '''
    https://developers.google.com/youtube/v3/live/docs/liveChatMessages/list
    '''
    url    = 'https://www.googleapis.com/youtube/v3/liveChat/messages'
    params = {'key': YT_API_KEY, 'liveChatId': chat_id, 'part': 'id,snippet,authorDetails'}
    if type(pageToken) == str:
        params['pageToken'] = pageToken

    data   = requests.get(url, params=params).json()

    try:
        first=None
        for item in data['items']:
            channelId = item['snippet']['authorChannelId']
            msg       = item['snippet']['displayMessage']
            usr       = item['authorDetails']['displayName']
            # supChat   = item['snippet']['superChatDetails']
            # supStic   = item['snippet']['superStickerDetails']
            # log_text  = '[by {}  https://www.youtube.com/channel/{}]\n  {}'.format(usr, channelId, msg)
            if msg.startswith(('req','rq','リク')):
                msg=re.sub(r'req\s*','', msg)
                msg=re.sub(r'rq\s*','', msg)
                msg=re.sub(r'リク\s.*','', msg)

                st.session_state.list.append(msg+" by"+usr)
                st.session_state.addnum+=1
        # print('start : ', data['items'][0]['snippet']['publishedAt'])
        # print('last_date   : ', data['items'][-1]['snippet']['publishedAt'])

    except:
        pass

    return data['nextPageToken']

def rewrite_sl(place):
    text=""
    for i in range(len(st.session_state.list)):
        text=text+'\\\n'+st.session_state.list[i]
    place.write(text)
    return

def main():

    slp_time        = 30 #sec

    st.title('リクエスト')
    st.subheader('rq/req/リクを先頭につけてリクエストしよう') 
    delete = st.button('先頭を消す')
    whileloop = st.toggle("更新開始/停止")
    place = st.empty()
    
    if delete:
        if(st.session_state.addnum>st.session_state.delnum):
        # delete
            del st.session_state.list[0]
            st.session_state.delnum+=1

    while whileloop:
        try:
            st.session_state.NextToken = get_chat(st.session_state.chat_id, st.session_state.NextToken)
            rewrite_sl(place)
            time.sleep(slp_time)
        except:
            pass
    rewrite_sl(place)
    
    # print('{}分後　終了予定'.format(take_time))
    # print('work on {}'.format(yt_url))


    
    # for ii in range(iter_times):
    #     #for jj in [0]:
    #     try:
    #         nextPageToken = get_chat(chat_id, nextPageToken, log_file)
    #         thread = threading.Thread(target=wait,args=(slp_time,))
    #         thread.start()
    #         thread.join()
    #     except:
    #         break

if __name__ == '__main__':
    if 'chat_id' not in st.session_state:
        st.session_state.chat_id=None
    while st.session_state.chat_id is None:
        # yt_url = input('Input YouTube URL > ')
        yt_url = st.text_input('Input URL of your stream')
        if st.button('send'):
            st.session_state.chat_id = get_chat_id(yt_url)
            st.session_state.list = []
            st.session_state.addnum =0
            st.session_state.delnum =0
            st.session_state.NextToken = None
        else:
            while True:
                time.sleep(1)

    main()
