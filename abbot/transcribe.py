import argparse
import os
import utils
import json # for writing dict into file

def transai():
    print('here we are')

    # load audio file name
    # audio_file_name="Der_Rat_fur_integrativen_Kapitalismus_Brandon_Smith.mp3"
    # audio_file_name="Stadt_Aschaffenburg_-_Lebendige_Stadt_mit_Zukunft_und_Tradition.mp3"
    # audio_file_name="Judge indicates portions of Mar-a-Lago search affidavit could be unsealed.mp3"
    # audio_file_name="World War II warships exposed as drought hits Danube River.mp3"
    # audio_file_name="Longtime_Trump_CFO_pleads_guilty_to_tax_fraud.mp3"
    # audio_file_name="What to know about northern lights that could be visible tonight.mp3"
    # audio_file_name="Liz Cheney reflects on political future after primary loss  Nightline.mp3"
    audio_file_name="kosmos.mp3"

    api_key = os.getenv("AAI_API_KEY")
    if api_key is None:
        raise RuntimeError("AAI_API_KEY environment variable not set. Try setting it now, or passing in your "
                               "API key as a command line argument with `--api_key`; check dima-pylog")

    # print(api_key)

    # Create header with authorization along with content-type
    header = {
        'authorization': api_key,
        'content-type': 'application/json'
    }

    print('...uploading the file...')
    upload_url = utils.upload_file('uploads/'+audio_file_name, header)
    print('...file uploaded...')

    # Request a transcription
    transcript_response = utils.request_transcript(upload_url, header)
    print('...transcription requested...')

    # Create a polling endpoint that will let us check when the transcription is complete
    polling_endpoint = utils.make_polling_endpoint(transcript_response)
    print('...polling endpoint created...')

    # Wait until the transcription is complete
    utils.wait_for_completion(polling_endpoint, header)
    print('...completion....')

    # Request the paragraphs of the transcript
    paragraphs = utils.get_paragraphs(polling_endpoint, header)
    print('...got paragraphs... \n\n\n')


#    audio_file_name="uploads/What to know about northern lights that could be visible tonight.mp3"

    x=audio_file_name.split('.')
    # text_file_name='transcript.txt'
    text_file_name='uploads/' +x[0] +'.txt'


    # Save and print transcript
    with open(text_file_name, 'w') as f:
        for para in paragraphs:
            print(para['text'] + '\n')
            f.write(para['text'] + '\n')

    para_html=[]
    for para in paragraphs:
        para_html.append(para['text'] )

    dump_file_name='uploads/'+ x[0] +'.dump'
    # save dump record
    with open(dump_file_name, 'w') as file:
        file.write(json.dumps(paragraphs)) # use `json.loads` to do the reverse



    return para_html 


if __name__ == '__main__':
    main()
