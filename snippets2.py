from __future__ import print_function
import uuid
import time
class SlidesSnippets(object):
    def __init__(self, service, credentials):
        self.service = service
        self.credentials = credentials

    def create_slide(self, presentation_id, page_id):
        slides_service = self.service
        # take the current number of slides
        presentation = slides_service.presentations().get(
            presentationId=presentation_id).execute()
        nslides = len(presentation.get('slides'))
        # insert a slide at the end
        requests = [
            {
                'createSlide': {
                    'objectId': page_id,
                    'insertionIndex': nslides-1,#tmp for Julie
                    'slideLayoutReference': {
                        'predefinedLayout': 'BLANK'
                    }
                }
            }
        ]
        # Execute the request.
        body = {
            'requests': requests
        }
        response = slides_service.presentations().batchUpdate(presentationId=presentation_id, body=body).execute()
        create_slide_response = response.get('replies')[0].get('createSlide')
        print('Created slide with ID: {0}'.format(
            create_slide_response.get('objectId')))
        return response
    
    def create_textbox_with_text(self, presentation_id, page_id, text, magnitudex, magnitudey, posx, posy, fontsize):
        slides_service = self.service
        # [START slides_create_textbox_with_text]
        # Create a new square textbox, using the supplied element ID.
        element_id = str(uuid.uuid4())
        requests = [
            {
                'createShape': {
                    'objectId': element_id,
                    'shapeType': 'TEXT_BOX',
                    'elementProperties': {
                        'pageObjectId': page_id,
                        'size': {
                            'height': {'magnitude': magnitudex, 'unit': 'PT'},
                            'width': {'magnitude': magnitudey, 'unit': 'PT'}
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': posx,
                            'translateY': posy,
                            'unit': 'PT'
                        }
                    }
                }
            },

            # Insert text into the box, using the supplied element ID.
            {
                'insertText': {
                    'objectId': element_id,
                    'insertionIndex': 0,
                    'text': text
                }
            },
            
            {
                'updateTextStyle': {
                    'objectId': element_id,
                    'style': {
                        'fontFamily': 'Times New Roman',
                        'fontSize': {
                            'magnitude': fontsize,
                            'unit': 'PT'
                        },
                        # 'foregroundColor': {
                        #     'opaqueColor': {
                        #         'rgbColor': {
                        #             'blue': 1.0,
                        #             'green': 0.0,
                        #             'red': 0.0
                        #         }
                        #     }
                        # }
                    },
                    'fields': 'fontSize'
                }
            }            
        ]

        # Execute the request.
        body = {
            'requests': requests
        }
        response = slides_service.presentations() \
            .batchUpdate(presentationId=presentation_id, body=body).execute()
        create_shape_response = response.get('replies')[0].get('createShape')
        print('Created textbox with ID: {0}'.format(
            create_shape_response.get('objectId')))
        # [END slides_create_textbox_with_text]
        return response    

    def create_textbox_with_bullets(self, presentation_id, page_id, text, magnitudex, magnitudey, posx, posy, fontsize):
        slides_service = self.service
        # [START slides_create_textbox_with_text]
        # Create a new square textbox, using the supplied element ID.
        element_id = str(uuid.uuid4())
        requests = [
            {
                'createShape': {
                    'objectId': element_id,
                    'shapeType': 'TEXT_BOX',
                    'elementProperties': {
                        'pageObjectId': page_id,
                        'size': {
                            'height': {'magnitude': magnitudex, 'unit': 'PT'},
                            'width': {'magnitude': magnitudey, 'unit': 'PT'}
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': posx,
                            'translateY': posy,
                            'unit': 'PT'
                        }
                    }
                }
            },

            # Insert text into the box, using the supplied element ID.
            {
                'insertText': {
                    'objectId': element_id,
                    'insertionIndex': 0,
                    'text': text
                }
            },
            
            {
                'updateTextStyle': {
                    'objectId': element_id,
                    'style': {
                        'fontFamily': 'Times New Roman',
                        'fontSize': {
                            'magnitude': fontsize,
                            'unit': 'PT'
                        },
                        # 'foregroundColor': {
                        #     'opaqueColor': {
                        #         'rgbColor': {
                        #             'blue': 1.0,
                        #             'green': 0.0,
                        #             'red': 0.0
                        #         }
                        #     }
                        # }
                    },
                    'fields': 'fontSize'
                }
            },
            {
                'createParagraphBullets': {
                    'objectId': element_id,
                    'textRange': {
                        'type': 'ALL'
                    },
                    'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE'
                }
            }
        ]

        # Execute the request.
        body = {
            'requests': requests
        }
        response = slides_service.presentations() \
            .batchUpdate(presentationId=presentation_id, body=body).execute()
        create_shape_response = response.get('replies')[0].get('createShape')
        print('Created textbox with ID: {0}'.format(
            create_shape_response.get('objectId')))
        # [END slides_create_textbox_with_text]
        return response    
    
    def create_image(self, presentation_id, page_id, IMAGE_URL, magnitudex, magnitudey, posx, posy):
        slides_service = self.service
        # [START slides_create_image]
        # Create a new image, using the supplied object ID,
        # with content downloaded from IMAGE_URL.
        requests = []
        image_id = str(uuid.uuid4())
        requests.append({
            'createImage': {
                'objectId': image_id,
                'url': IMAGE_URL,
                'elementProperties': {
                    'pageObjectId': page_id,
                    'size': {
                        'height': {'magnitude': magnitudey, 'unit': 'PT'},
                        'width': {'magnitude': magnitudex, 'unit': 'PT'},
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': posx,
                        'translateY': posy,
                        'unit': 'PT'
                    }
                }
            }
        })

        # Execute the request.
        body = {
            'requests': requests
        }
        for k in range(40):      
            print(f'Attempt adding image {k+1}/20')      
            try:            
                response = slides_service.presentations() \
                    .batchUpdate(presentationId=presentation_id, body=body).execute()
                create_image_response = response.get('replies')[0].get('createImage')
                print('Created image with ID: {0}'.format(
                create_image_response.get('objectId')))        
                return response
            except Exception:
                continue
        print('Image was not added')
        

    def create_images(self, presentation_id, page_id, image_urls, magnitudex, magnitudey, posx, posy):
        slides_service = self.service
        # [START slides_create_image]
        # Create a new image, using the supplied object ID,
        print(image_urls)
        requests = []
        for k in range(len(image_urls)):
            image_id = str(uuid.uuid4())
            requests.append({
                'createImage': {
                    'objectId': image_id,
                    'url': image_urls[k],
                    'elementProperties': {
                        'pageObjectId': page_id,
                        'size': {
                            'height': {'magnitude': magnitudey[k], 'unit': 'PT'},
                            'width': {'magnitude': magnitudex[k], 'unit': 'PT'},
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': posx[k],
                            'translateY': posy[k],
                            'unit': 'PT'
                        }
                    }
                }
            })

        # Execute the request.
        body = {
            'requests': requests
        }
        query = slides_service.presentations() \
            .batchUpdate(presentationId=presentation_id, body=body)
        response = query.execute()
        create_image_response = response.get('replies')[0].get('createImage')
        print('Created image with ID: {0}'.format(
        create_image_response.get('objectId')))        
        
        