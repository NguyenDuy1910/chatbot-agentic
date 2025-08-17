#!/usr/bin/env python3
"""
Test script to verify model structure without database dependencies
"""

import sys
import os
import time

# Mock the database dependencies
class MockBase:
    pass

class MockColumn:
    def __init__(self, *args, **kwargs):
        pass

class MockJSONField:
    def __init__(self, *args, **kwargs):
        pass

class MockString:
    pass

class MockText:
    pass

class MockBigInteger:
    pass

class MockBoolean:
    pass

class MockForeignKey:
    def __init__(self, *args, **kwargs):
        pass

# Mock modules
sys.modules['supabase'] = type(sys)('supabase')
sys.modules['sqlalchemy'] = type(sys)('sqlalchemy')
sys.modules['sqlalchemy.orm'] = type(sys)('sqlalchemy.orm')
sys.modules['sqlalchemy.ext'] = type(sys)('sqlalchemy.ext')
sys.modules['sqlalchemy.ext.declarative'] = type(sys)('sqlalchemy.ext.declarative')
sys.modules['pydantic'] = type(sys)('pydantic')

# Mock SQLAlchemy
sqlalchemy = sys.modules['sqlalchemy']
sqlalchemy.Column = MockColumn
sqlalchemy.String = MockString
sqlalchemy.Text = MockText
sqlalchemy.BigInteger = MockBigInteger
sqlalchemy.Boolean = MockBoolean
sqlalchemy.ForeignKey = MockForeignKey

# Mock Pydantic
pydantic = sys.modules['pydantic']
class MockBaseModel:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    
    def model_dump(self):
        return {}
    
    @classmethod
    def model_validate(cls, obj):
        return cls()

class MockConfigDict:
    def __init__(self, **kwargs):
        pass

pydantic.BaseModel = MockBaseModel
pydantic.ConfigDict = MockConfigDict

def test_model_structure():
    """Test that models can be imported and instantiated"""
    print("Testing model structure...")
    
    models_to_test = [
        ('users', ['User', 'UserModel', 'Users']),
        ('chats', ['Chat', 'ChatModel', 'Chats', 'Folder', 'FolderModel', 'Folders']),
        ('groups', ['Group', 'GroupModel', 'Groups']),
        ('channels', ['Channel', 'ChannelModel', 'Channels']),
        ('messages', ['Message', 'MessageModel', 'Messages', 'MessageReaction', 'MessageReactionModel', 'MessageReactions']),
        ('files', ['File', 'FileModel', 'Files']),
        ('models', ['Model', 'ModelModel', 'Models']),
        ('tags', ['Tag', 'TagModel', 'Tags']),
        ('memories', ['Memory', 'MemoryModel', 'Memories']),
        ('feedback', ['Feedback', 'FeedbackModel', 'Feedbacks']),
        ('connections', ['Connection', 'ConnectionModel', 'Connections']),
    ]
    
    success_count = 0
    total_count = len(models_to_test)
    
    for module_name, class_names in models_to_test:
        try:
            print(f"\n{module_name.upper()} MODEL:")
            
            # Import the module
            module = __import__(f'finx.models.{module_name}', fromlist=class_names)
            
            # Check each class
            for class_name in class_names:
                if hasattr(module, class_name):
                    cls = getattr(module, class_name)
                    print(f"  ✓ {class_name} - Found")
                    
                    # Try to create instance for Model classes (not Table classes)
                    if class_name.endswith('Model'):
                        try:
                            # Create a test instance
                            if class_name == 'UserModel':
                                instance = cls(
                                    id="test-id",
                                    name="Test User",
                                    email="test@example.com",
                                    role="user",
                                    profile_image_url="/user.png",
                                    last_active_at=int(time.time()),
                                    updated_at=int(time.time()),
                                    created_at=int(time.time())
                                )
                            elif class_name == 'ChatModel':
                                instance = cls(
                                    id="test-id",
                                    user_id="test-user",
                                    title="Test Chat",
                                    created_at=int(time.time()),
                                    updated_at=int(time.time())
                                )
                            elif class_name == 'FolderModel':
                                instance = cls(
                                    id="test-id",
                                    user_id="test-user",
                                    name="Test Folder",
                                    created_at=int(time.time()),
                                    updated_at=int(time.time())
                                )
                            else:
                                # Generic test for other models
                                instance = cls(
                                    id="test-id",
                                    user_id="test-user",
                                    created_at=int(time.time()),
                                    updated_at=int(time.time())
                                )
                            print(f"    ✓ {class_name} instance created successfully")
                        except Exception as e:
                            print(f"    ⚠ {class_name} instance creation failed: {e}")
                else:
                    print(f"  ✗ {class_name} - Not found")
            
            success_count += 1
            print(f"  ✓ {module_name} module imported successfully")
            
        except Exception as e:
            print(f"  ✗ {module_name} module import failed: {e}")
    
    print(f"\n{'='*50}")
    print(f"RESULTS: {success_count}/{total_count} modules imported successfully")
    print(f"{'='*50}")
    
    return success_count == total_count

if __name__ == "__main__":
    success = test_model_structure()
    sys.exit(0 if success else 1)
