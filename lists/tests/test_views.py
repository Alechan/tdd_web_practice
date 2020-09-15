import unittest
from unittest.mock import patch, Mock

from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import escape

from lists.forms import ExistingListItemForm, EMPTY_ITEM_ERROR, DUPLICATE_ITEM_ERROR, ItemForm
from lists.models import List, Item
from lists.tests.base import DjangoTestCase
from lists.views import new_list

User = get_user_model()


class HomePageTest(DjangoTestCase):

    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_home_page_uses_item_form(self):
        response = self.client.get("/")
        self.assertIsInstance(response.context["form"], ItemForm)


class ListViewTest(DjangoTestCase):
    def test_passes_correct_list_to_template(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.get(f'/lists/{correct_list.id}/')
        self.assertEqual(response.context['list'], correct_list)

    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertTemplateUsed(response, 'list.html')

    def test_displays_only_items_for_that_list(self):
        correct_list = List.objects.create()
        Item.objects.create(text='itemey 1', list=correct_list)
        Item.objects.create(text='itemey 2', list=correct_list)
        other_list = List.objects.create()
        Item.objects.create(text='other list item 1', list=other_list)
        Item.objects.create(text='other list item 2', list=other_list)

        response = self.client.get(f'/lists/{correct_list.id}/')

        self.assertContains(response, 'itemey 1')
        self.assertContains(response, 'itemey 2')
        self.assertNotContains(response, 'other list item 1')
        self.assertNotContains(response, 'other list item 2')
    
    def test_for_invalid_input_nothing_saved_to_bd(self):
        self.post_invalid_input()
        self.assertEqual(Item.objects.count(), 0)

    def test_for_invalid_input_renders_list_template(self):
        response = self.post_invalid_input()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "list.html")

    def test_for_invalid_input_passes_form_to_template(self):
        response = self.post_invalid_input()
        self.assertIsInstance(response.context["form"], ExistingListItemForm)

    def test_for_invalid_input_shows_error_on_page(self):
        response = self.post_invalid_input()
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_displays_item_form(self):
        list_ = List.objects.create()
        response = self.client.get(f"/lists/{list_.id}/")
        self.assertIsInstance(response.context["form"], ExistingListItemForm)

    def test_duplicate_item_validation_errors_end_up_on_lists_page(self):
        list1 = List.objects.create()
        item1 = Item.objects.create(list=list1, text="textey")
        response = self.client.post(
            f"/lists/{list1.id}/",
            data={"text": "textey"}
        )
        expected_error = escape(DUPLICATE_ITEM_ERROR)
        self.assertContains(response, expected_error)
        self.assertTemplateUsed(response, "list.html")
        self.assertEqual(Item.objects.all().count(), 1)

    def test_valid_share_form(self):
        list_ = List.create_new(first_item_text="hello Manolow")

        response = self.client.get(f"/lists/{list_.id}/")

        dom = self.get_DOM_for_response(response)

        share_form = dom.find('form', {'id': 'form_share'})
        share_list_url = reverse("share_list", args=(list_.id,))

        self.assertIsNotNone(share_form)
        self.assertEqual(share_form.get("method"), "POST")
        self.assertEqual(share_form.get("action"), share_list_url)

        self.assertFormContainsValidInput(share_form, input_id="sharee", input_type="email")
        self.assertFormContainsValidSubmitButton(share_form)
        self.assertFormContainsValidCSRFToken(share_form)

    def test_includes_shared_with_list(self):
        owner    = User.objects.create(email='owner@d.com')
        list_ = List.create_new(first_item_text="1rst item", owner=owner)
        sharee_1 = User.objects.create(email='sharee-1@d.com')
        sharee_2 = User.objects.create(email='sharee-2@d.com')
        _        = User.objects.create(email='irrelevant@d.com')
        list_.shared_with.set([sharee_1, sharee_2])

        response = self.client.get(f"/lists/{list_.id}/")
        dom = self.get_DOM_for_response(response)
        shared_with_list = dom.select(".list-sharee")
        self.assertEqual(len(shared_with_list), 2)
        shared_with_list_emails = [e.text for e in shared_with_list]
        self.assertIn(sharee_1.email, shared_with_list_emails)
        self.assertIn(sharee_2.email, shared_with_list_emails)

    def post_invalid_input(self):
        list_ = List.objects.create()
        response = self.client.post(
            f'/lists/{list_.id}/',
            data={'text': ''}
        )
        return response


class NewListViewIntegratedTest(DjangoTestCase):
    def test_can_save_a_POST_request(self):
        self.client.post('/lists/new', data={'text': 'A new list item'})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list item')

    def test_redirects_after_POST(self):
        response = self.client.post('/lists/new', data={'text': 'A new list item'})
        new_list = List.objects.first()
        self.assertRedirects(response, f'/lists/{new_list.id}/')

    def test_can_save_a_POST_request_to_an_existing_list(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
            f'/lists/{correct_list.id}/',
            data={'text': 'A new item for an existing list'}
        )

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new item for an existing list')
        self.assertEqual(new_item.list, correct_list)

    def test_POST_redirects_to_list_view(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(
            f'/lists/{correct_list.id}/',
            data={'text': 'A new item for an existing list'}
        )

        self.assertRedirects(response, f'/lists/{correct_list.id}/')

    def test_for_invalid_input_renders_home_template(self):
        response = self.client.post("/lists/new", data={"text": ""})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")

    def test_validation_errors_are_shown_on_home_page(self):
        response = self.client.post("/lists/new", data={"text": ""})
        expected_error = escape(EMPTY_ITEM_ERROR)
        self.assertContains(response, expected_error)

    def test_for_invalid_input_passes_from_to_template(self):
        response = self.client.post("/lists/new", data={"text": ""})
        self.assertIsInstance(response.context["form"], ItemForm)

    def test_list_owner_is_saved_if_user_is_authenticated(self):
        user = User.objects.create(email='a@b.com')
        self.client.force_login(user)
        self.client.post('/lists/new', data={'text': 'new item'})
        list_ = List.objects.first()
        self.assertEqual(list_.owner, user)


class MyListsTest(DjangoTestCase):
    def test_my_lists_url_renders_my_lists_template(self):
        User.objects.create(email='a@b.com')
        response = self.client.get('/lists/users/a@b.com/')
        self.assertTemplateUsed(response, 'my_lists.html')
    
    def test_passes_correct_owner_to_template(self):
        User.objects.create(email='wrong@owner.com')
        correct_user = User.objects.create(email='a@b.com')
        response = self.client.get('/lists/users/a@b.com/')
        self.assertEqual(response.context['owner'], correct_user)

    def test_shows_correct_personal_lists(self):
        owner = User.objects.create(email="owner@d.com")
        list_1 = List.create_new(first_item_text="1rst list", owner=owner)
        list_2 = List.create_new(first_item_text="2nd list", owner=owner)
        _ = List.create_new(first_item_text="irrelevant list")
        lists = [list_1, list_2]

        response = self.client.get(f'/lists/users/{owner.email}/')

        heading_text = f"{owner}'s lists"

        self.assertListCollectionIsValid(response, heading_text, lists)

    def assertListCollectionIsValid(self, response, heading_text, lists):
        dom = self.get_DOM_for_response(response)
        lists_h2 = dom.find("h2", text=heading_text)
        self.assertIsNotNone(lists_h2)
        ul_items = lists_h2.find_next("ul")
        self.assertIsNotNone(ul_items)
        lists_anchors = ul_items.find_all("a")
        self.assertEqual(len(lists_anchors), 2)

        def list_anchor_matcher(list_):
            return lambda a: a.text == list_.item_set.first().text and a.get("href") == list_.get_absolute_url()

        for list_ in lists:
            self.assertExactlyOne(
                list_anchor_matcher(list_),
                lists_anchors
            )

    def assertExactlyOne(self, element_matcher, container):
        matches = list(filter(element_matcher, container))
        if len(matches) < 1:
            self.fail(f"No element satisfied the matcher in {container}")
        elif len(matches) > 2:
            self.fail(f"More than one element ({matches}) satisfied the matcher in {container}")




@patch('lists.views.NewListForm')
class NewListViewUnitTest(unittest.TestCase):
    def setUp(self):
        self.request = HttpRequest()
        self.request.POST['text'] = 'new list item'
        self.request.user = Mock()

    def test_passes_POST_data_to_NewListForm(self, mockNewListForm):
        new_list(self.request)
        mockNewListForm.assert_called_once_with(data=self.request.POST)

    @patch('lists.views.redirect')
    def test_redirects_to_form_returned_object_if_form_valid(
            self, mock_redirect, mockNewListForm
    ):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = True

        response = new_list(self.request)

        self.assertEqual(response, mock_redirect.return_value)
        mock_redirect.assert_called_once_with(mock_form.save.return_value)
    
    @patch('lists.views.render')
    def test_renders_home_template_with_form_if_form_invalid(
        self, mock_render, mockNewListForm
    ):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = False

        response = new_list(self.request)

        self.assertEqual(response, mock_render.return_value)
        mock_render.assert_called_once_with(
            self.request, 'home.html', {'form': mock_form}
        )

    def test_does_not_save_if_form_invalid(self, mockNewListForm):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = False
        new_list(self.request)
        self.assertFalse(mock_form.save.called)


class ShareListTest(DjangoTestCase):
    def setUp(self):
        self.request = HttpRequest()
        self.request.POST['sharee'] = 'new list item'
        self.request.user = Mock()

    def test_post_redirects_to_lists_page(self):
        sharee_email = 'share-recipient@example.com'
        sharee = User.objects.create(email=sharee_email)
        owner_email = 'a@b.com'
        owner = User.objects.create(email=owner_email)
        list_ = List.objects.create(owner=owner)
        self.client.force_login(owner)

        self.client.post(f'/lists/{list_.id}/share', data={'sharee': sharee_email})

        self.assertIn(sharee, list_.shared_with.all())


