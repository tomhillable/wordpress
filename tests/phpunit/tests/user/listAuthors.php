<?php
/**
 * @group author
 * @group user
 */
class Tests_User_ListAuthors extends WP_UnitTestCase {
	var $users = array();
	var $user_urls = array();
		/* Defaults
		'orderby'       => 'name',
		'order'         => 'ASC',
		'number'        => null,
		'optioncount'   => false,
		'exclude_admin' => true,
		'show_fullname' => false,
		'hide_empty'    => true,
		'echo'          => true,
		'feed'          => [empty string],
		'feed_image'    => [empty string],
		'feed_type'     => [empty string],
		'style'         => 'list',
		'html'          => true );
		*/
	function setUp() {
		parent::setUp();
		$this->users[] = $this->factory->user->create( array( 'user_login' => 'zack', 'display_name' => 'zack', 'role' => 'author', 'first_name' => 'zack', 'last_name' => 'moon' ) );
		$this->users[] = $this->factory->user->create( array( 'user_login' => 'bob', 'display_name' => 'bob', 'role' => 'author', 'first_name' => 'bob', 'last_name' => 'reno' ) );
		$this->users[] = $this->factory->user->create( array( 'user_login' => 'paul', 'display_name' => 'paul', 'role' => 'author', 'first_name' => 'paul', 'last_name' => 'norris' ) );
		$count = 0;
		foreach ( $this->users as $userid ) {
			$count = $count + 5;
			for ( $i = 0; $i < $count; $i++ ) {
				$this->factory->post->create( array( 'post_type' => 'post', 'post_author' => $userid ) );
			}

			$this->user_urls[] = get_author_posts_url( $userid );
		}
	}

	function test_wp_list_authors_default() {
		$expected['default'] = '<li><a href="' . $this->user_urls[1] . '" title="Posts by bob">bob</a></li><li><a href="' . $this->user_urls[2] . '" title="Posts by paul">paul</a></li><li><a href="' . $this->user_urls[0] . '" title="Posts by zack">zack</a></li>';
		$this->AssertEquals( $expected['default'], wp_list_authors( array( 'echo' => false ) ) );
	}

	function test_wp_list_authors_orderby() {
		$expected['post_count'] = '<li><a href="' . $this->user_urls[0] . '" title="Posts by zack">zack</a></li><li><a href="' . $this->user_urls[1] . '" title="Posts by bob">bob</a></li><li><a href="' . $this->user_urls[2] . '" title="Posts by paul">paul</a></li>';
		$this->AssertEquals( $expected['post_count'], wp_list_authors( array( 'echo' => false, 'orderby' => 'post_count' ) ) );
	}

	function test_wp_list_authors_order() {
		$expected['id'] = '<li><a href="' . $this->user_urls[2] . '" title="Posts by paul">paul</a></li><li><a href="' . $this->user_urls[1] . '" title="Posts by bob">bob</a></li><li><a href="' . $this->user_urls[0] . '" title="Posts by zack">zack</a></li>';
		$this->AssertEquals( $expected['id'], wp_list_authors( array( 'echo' => false, 'orderby' => 'id', 'order' => 'DESC' ) ) );
	}

	function test_wp_list_authors_optioncount() {
		$expected['optioncount'] = '<li><a href="' . $this->user_urls[1] . '" title="Posts by bob">bob</a> (10)</li><li><a href="' . $this->user_urls[2] . '" title="Posts by paul">paul</a> (15)</li><li><a href="' . $this->user_urls[0] . '" title="Posts by zack">zack</a> (5)</li>';
		$this->AssertEquals( $expected['optioncount'], wp_list_authors( array( 'echo' => false, 'optioncount' => 1 ) ) );
	}

	function test_wp_list_authors_exclude_admin() {
		$this->factory->post->create( array( 'post_type' => 'post', 'post_author' => 1 ) );
		$expected['exclude_admin'] = '<li><a href="' . get_author_posts_url( 1 ) . '" title="Posts by admin">admin</a></li><li><a href="' . $this->user_urls[1] . '" title="Posts by bob">bob</a></li><li><a href="' . $this->user_urls[2] . '" title="Posts by paul">paul</a></li><li><a href="' . $this->user_urls[0] . '" title="Posts by zack">zack</a></li>';
		$this->AssertEquals( $expected['exclude_admin'], wp_list_authors( array( 'echo' => false, 'exclude_admin' => 0 ) ) );
	}

	function test_wp_list_authors_show_fullname() {
		$expected['show_fullname'] = '<li><a href="' . $this->user_urls[1] . '" title="Posts by bob">bob reno</a></li><li><a href="' . $this->user_urls[2] . '" title="Posts by paul">paul norris</a></li><li><a href="' . $this->user_urls[0] . '" title="Posts by zack">zack moon</a></li>';
		$this->AssertEquals( $expected['show_fullname'], wp_list_authors( array( 'echo' => false, 'show_fullname' => 1 ) ) );
	}

	function test_wp_list_authors_hide_empty() {
		$fred_id = $this->factory->user->create( array( 'user_login' => 'fred', 'role' => 'author' ) );
		$expected['hide_empty'] = '<li><a href="' . $this->user_urls[1] . '" title="Posts by bob">bob</a></li><li><a href="' . get_author_posts_url( $fred_id ) . '" title="Posts by fred">fred</a></li><li><a href="' . $this->user_urls[2] . '" title="Posts by paul">paul</a></li><li><a href="' . $this->user_urls[0] . '" title="Posts by zack">zack</a></li>';
		$this->AssertEquals( $expected['hide_empty'], wp_list_authors( array( 'echo' => false, 'hide_empty' => 0 ) ) );
	}

	function test_wp_list_authors_echo() {
		$expected['echo'] = '<li><a href="' . $this->user_urls[1] . '" title="Posts by bob">bob</a></li><li><a href="' . $this->user_urls[2] . '" title="Posts by paul">paul</a></li><li><a href="' . $this->user_urls[0] . '" title="Posts by zack">zack</a></li>';
		ob_start();
		wp_list_authors( array( 'echo' => true ) );
		$actual = ob_get_clean();
		$this->AssertEquals( $expected['echo'], $actual );
	}

	function test_wp_list_authors_feed() {
		$expected['feed'] = '<li><a href="' . $this->user_urls[1] . '" title="Posts by bob">bob</a> (<a href="http://' . WP_TESTS_DOMAIN . '/?feed=rss2&amp;author=' . $this->users[1] . '">link to feed</a>)</li><li><a href="' . $this->user_urls[2] . '" title="Posts by paul">paul</a> (<a href="http://' . WP_TESTS_DOMAIN . '/?feed=rss2&amp;author=' . $this->users[2] . '">link to feed</a>)</li><li><a href="' . $this->user_urls[0] . '" title="Posts by zack">zack</a> (<a href="http://' . WP_TESTS_DOMAIN . '/?feed=rss2&amp;author=' . $this->users[0] . '">link to feed</a>)</li>';
		$this->AssertEquals( $expected['feed'], wp_list_authors( array( 'echo' => false, 'feed' => 'link to feed' ) ) );
	}

	function test_wp_list_authors_feed_image() {
		$expected['feed_image'] = '<li><a href="' . $this->user_urls[1] . '" title="Posts by bob">bob</a> <a href="http://' . WP_TESTS_DOMAIN . '/?feed=rss2&amp;author=' . $this->users[1] . '"><img src="http://' . WP_TESTS_DOMAIN . '/path/to/a/graphic.png" style="border: none;" /></a></li><li><a href="' . $this->user_urls[2] . '" title="Posts by paul">paul</a> <a href="http://' . WP_TESTS_DOMAIN . '/?feed=rss2&amp;author=' . $this->users[2] . '"><img src="http://' . WP_TESTS_DOMAIN . '/path/to/a/graphic.png" style="border: none;" /></a></li><li><a href="' . $this->user_urls[0] . '" title="Posts by zack">zack</a> <a href="http://' . WP_TESTS_DOMAIN . '/?feed=rss2&amp;author=' . $this->users[0] . '"><img src="http://' . WP_TESTS_DOMAIN . '/path/to/a/graphic.png" style="border: none;" /></a></li>';
		$this->AssertEquals( $expected['feed_image'], wp_list_authors( array( 'echo' => false, 'feed_image' => WP_TESTS_DOMAIN . '/path/to/a/graphic.png' ) ) );
	}

	/**
	 * @ticket 26538
	 */
	function test_wp_list_authors_feed_type() {
		$expected['feed_type'] = '<li><a href="' . $this->user_urls[1] . '" title="Posts by bob">bob</a> (<a href="http://' . WP_TESTS_DOMAIN . '/?feed=atom&amp;author=' . $this->users[1] . '">link to feed</a>)</li><li><a href="' . $this->user_urls[2] . '" title="Posts by paul">paul</a> (<a href="http://' . WP_TESTS_DOMAIN . '/?feed=atom&amp;author=' . $this->users[2] . '">link to feed</a>)</li><li><a href="' . $this->user_urls[0] . '" title="Posts by zack">zack</a> (<a href="http://' . WP_TESTS_DOMAIN . '/?feed=atom&amp;author=' . $this->users[0] . '">link to feed</a>)</li>';
		$this->AssertEquals( $expected['feed_type'], wp_list_authors( array( 'echo' => false, 'feed' => 'link to feed', 'feed_type' => 'atom' ) ) );
	}

	function test_wp_list_authors_style() {
		$expected['style'] = '<a href="' . $this->user_urls[1] . '" title="Posts by bob">bob</a>, <a href="' . $this->user_urls[2] . '" title="Posts by paul">paul</a>, <a href="' . $this->user_urls[0] . '" title="Posts by zack">zack</a>';
		$this->AssertEquals( $expected['style'], wp_list_authors( array( 'echo' => false, 'style' => 'none' ) ) );
	}

	function test_wp_list_authors_html() {
		$expected['html'] = 'bob, paul, zack';
		$this->AssertEquals( $expected['html'], wp_list_authors( array( 'echo' => false, 'html' => 0 ) ) );
	}

}
